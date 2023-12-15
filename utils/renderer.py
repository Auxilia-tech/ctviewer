from vedo import Plotter
from vedo.pyplot import np, CornerHistogram
from vedo.colors import color_map, get_color
import vedo


class CustomIsosurfaceBrowser(Plotter):
    """
    Generate a Volume isosurfacing controlled by a slider.
    """

    def __init__(
        self,
        volume,
        isovalue=None,
        c=None,
        alpha=1,
        lego=False,
        res=50,
        use_gpu=False,
        precompute=False,
        progress=False,
        cmap="hot",
        delayed=False,
        sliderpos=4,
        pos=(0, 0),
        size="auto",
        screensize="auto",
        title="",
        bg="white",
        bg2=None,
        axes=1,
        interactive=True,
        qt_widget=None
    ):
        """
        Generate a `vedo.Plotter` for Volume isosurfacing using a slider.

        Set `delayed=True` to delay slider update on mouse release.

        Set `res` to set the resolution, e.g. the number of desired isosurfaces to be
        generated on the fly.

        Set `precompute=True` to precompute the isosurfaces (so slider browsing will be smoother).

        Examples:
            - [app_isobrowser.py](https://github.com/marcomusy/vedo/tree/master/examples/volumetric/app_isobrowser.py)

                ![](https://vedo.embl.es/images/advanced/app_isobrowser.gif)
        """

        super().__init__(
            pos=pos,
            bg=bg,
            bg2=bg2,
            size=size,
            screensize=screensize,
            title=title,
            interactive=interactive,
            axes=axes,
            qt_widget=qt_widget
        )

        ### GPU ################################
        if use_gpu and hasattr(volume.properties, "GetIsoSurfaceValues"):

            scrange = volume.scalar_range()
            delta = scrange[1] - scrange[0]
            if not delta:
                return

            if isovalue is None:
                isovalue = delta / 3.0 + scrange[0]

            # isovalue slider callback
            def slider_isovalue(widget, event):
                value = widget.GetRepresentation().GetValue()
                isovals.SetValue(0, value)

            isovals = volume.properties.GetIsoSurfaceValues()
            isovals.SetValue(0, isovalue)
            self.add(volume.mode(5).alpha(alpha).cmap(c))

            self.add_slider(
                slider_isovalue,
                scrange[0] + 0.02 * delta,
                scrange[1] - 0.02 * delta,
                value=isovalue,
                pos=sliderpos,
                title="scalar value",
                show_value=True,
                delayed=delayed,
            )

        ### CPU ################################
        else:

            self._prev_value = 1e30

            scrange = volume.scalar_range()
            delta = scrange[1] - scrange[0]
            if not delta:
                return

            if lego:
                res = int(res / 2)  # because lego is much slower
                slidertitle = ""
            else:
                slidertitle = "scalar value"

            allowed_vals = np.linspace(scrange[0], scrange[1], num=res)

            bacts = {}  # cache the meshes so we dont need to recompute
            if precompute:
                delayed = False  # no need to delay the slider in this case
                if progress:
                    pb = vedo.ProgressBar(0, len(allowed_vals), delay=1)

                for value in allowed_vals:
                    value_name = vedo.utils.precision(value, 2)
                    if lego:
                        mesh = volume.legosurface(vmin=value)
                        if mesh.ncells:
                            mesh.cmap(cmap, vmin=scrange[0], vmax=scrange[1], on="cells")
                    else:
                        mesh = volume.isosurface(value).color(c).alpha(alpha)
                    bacts.update({value_name: mesh})  # store it
                    if progress:
                        pb.print("isosurfacing volume..")

            # isovalue slider callback
            def slider_isovalue(widget, event):

                prevact = self.actors[0]
                if isinstance(widget, float):
                    value = widget
                else:
                    value = widget.GetRepresentation().GetValue()

                # snap to the closest
                idx = (np.abs(allowed_vals - value)).argmin()
                value = allowed_vals[idx]

                if abs(value - self._prev_value) / delta < 0.001:
                    return
                self._prev_value = value

                value_name = vedo.utils.precision(value, 2)
                if value_name in bacts:  # reusing the already existing mesh
                    # print('reusing')
                    mesh = bacts[value_name]
                else:  # else generate it
                    # print('generating', value)
                    if lego:
                        mesh = volume.legosurface(vmin=value)
                        if mesh.ncells:
                            mesh.cmap(cmap, vmin=scrange[0], vmax=scrange[1], on="cells")
                    else:
                        mesh = volume.isosurface(value).color(c).alpha(alpha)
                    bacts.update({value_name: mesh})  # store it

                self.renderer.RemoveActor(prevact)
                self.renderer.AddActor(mesh)
                self.actors[0] = mesh

            ################################################

            if isovalue is None:
                isovalue = delta / 3.0 + scrange[0]

            self.actors = [None]
            slider_isovalue(isovalue, "")  # init call
            if lego:
                self.actors[0].add_scalarbar(pos=(0.8, 0.12))

            self.add_slider(
                slider_isovalue,
                scrange[0] + 0.02 * delta,
                scrange[1] - 0.02 * delta,
                value=isovalue,
                pos=sliderpos,
                title=slidertitle,
                show_value=True,
                delayed=delayed,
            )


class CustomRayCastPlotter(Plotter):
    """
    Generate Volume rendering using ray casting.
    """

    def __init__(self, volume, **kwargs):
        """
        Generate a window for Volume rendering using ray casting.

        Returns:
            `vedo.Plotter` object.

        Examples:
            - [app_raycaster.py](https://github.com/marcomusy/vedo/tree/master/examples/volumetric/app_raycaster.py)

            ![](https://vedo.embl.es/images/advanced/app_raycaster.gif)
        """

        super().__init__(**kwargs)

        self.alphaslider0 = 1
        self.alphaslider1 = 0.7
        self.alphaslider2 = 1

        self.properties = volume.properties
        img = volume.dataset

        if volume.dimensions()[2] < 3:
            vedo.logger.error("RayCastPlotter: not enough z slices.")
            raise RuntimeError

        self.smin, self.smax = img.GetScalarRange()
        self.x0alpha = self.smin + (self.smax - self.smin) * 0.25
        self.x1alpha = self.smin + (self.smax - self.smin) * 0.5
        self.x2alpha = self.smin + (self.smax - self.smin) * 1.0

        # color map slider
        # Create transfer mapping scalar value to color
        cmaps = [
            "jet",
            "viridis",
            "bone",
            "hot",
            "plasma",
            "winter",
            "cool",
            "gist_earth",
            "coolwarm",
            "tab10",
        ]
        cols_cmaps = []
        for cm in cmaps:
            cols = color_map(range(0, 21), cm, 0, 20)  # sample 20 colors
            cols_cmaps.append(cols)
        # Ncols = len(cmaps)
        csl = (0.9, 0.9, 0.9)
        if sum(get_color(self.renderer.GetBackground())) > 1.5:
            csl = (0.1, 0.1, 0.1)

        # alpha sliders
        # Create transfer mapping scalar value to opacity
        self.opacityTransferFunction = self.properties.GetScalarOpacity()

        self.setOTF()

        def sliderA0(widget, event):
            self.alphaslider0 = widget.GetRepresentation().GetValue()
            self.setOTF()

        self.w0 = self.add_slider(
            sliderA0,
            0,
            1,
            value=self.alphaslider0,
            pos=[(0.8, 0.1), (0.8, 0.26)],
            c=csl,
            show_value=0,
        )

        def sliderA1(widget, event):
            self.alphaslider1 = widget.GetRepresentation().GetValue()
            self.setOTF()

        self.add_slider(
            sliderA1,
            0,
            1,
            value=self.alphaslider1,
            pos=[(0.85, 0.1), (0.85, 0.26)],
            c=csl,
            show_value=0,
        )

        def sliderA2(widget, event):
            self.alphaslider2 = widget.GetRepresentation().GetValue()
            self.setOTF()

        w2 = self.add_slider(
            sliderA2,
            0,
            1,
            value=self.alphaslider2,
            pos=[(0.90, 0.1), (0.90, 0.26)],
            c=csl,
            show_value=0,
            # title="Opacity levels",
        )
        # w2.GetRepresentation().SetTitleHeight(0.014)

        # add a button
        def button_func_mode(_obj, _ename):
            s = volume.mode()
            snew = (s + 1) % 2
            print(snew)
            volume.mode(snew)
            self.bum.switch()

        self.bum = self.add_button(
            button_func_mode,
            pos=(0.5, 1),
            states=["composite", "max proj."],
            c=["bb", "gray"],
            bc=["gray", "bb"],  # colors of states
            font="",
            size=24,
            bold=0,
            italic=False,
        )
        self.bum.frame(color='w')
        self.bum.status(volume.mode())

        # add histogram of scalar
        plot = CornerHistogram(
            volume,
            bins=25,
            logscale=1,
            c=(0.7, 0.7, 0.7),
            bg=(0.7, 0.7, 0.7),
            pos=(0.76, 0.065),
            lines=True,
            dots=False,
            nmax=3.1415e06,  # subsample otherwise is too slow
            title='Volume Histogram'
        )

        plot.GetPosition2Coordinate().SetValue(0.197, 0.20, 0)
        plot.GetXAxisActor2D().SetFontFactor(0.7)
        plot.GetProperty().SetOpacity(0.5)
        self.add([plot, volume])

    def setOTF(self):
        self.opacityTransferFunction.RemoveAllPoints()
        self.opacityTransferFunction.AddPoint(self.smin, 0.0)
        self.opacityTransferFunction.AddPoint(self.smin + (self.smax - self.smin) * 0.1, 0.0)
        self.opacityTransferFunction.AddPoint(self.x0alpha, self.alphaslider0)
        self.opacityTransferFunction.AddPoint(self.x1alpha, self.alphaslider1)
        self.opacityTransferFunction.AddPoint(self.x2alpha, self.alphaslider2)
