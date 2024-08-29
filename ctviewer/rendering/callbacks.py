class RendererCallbacks:
    """A class that provides callbacks for rendering objects."""

    def __init__(self, renderer):
        """Initialize the RendererCallbacks class.

        Args:
            renderer: The renderer object to associate with the callbacks.
        """
        self.renderer = renderer
    
    def add(self, obj):
        """Add an object to the renderer.

        Args:
            obj: The object to add to the renderer.
        """
        self.renderer.add(obj)

    def background(self):
        """Get the background of the renderer.

        Returns:
            The background of the renderer.
        """
        return self.renderer.background()

    def render(self):
        """Render the renderer."""
        self.renderer.render()

    def add_slider(self, *args, **kwargs):
        """Add a slider to the renderer.

        Returns:
            The added slider object.
        """
        return self.renderer.add_slider(*args, **kwargs)

    def add_slider3d(self, *args, **kwargs):
        """Add a 3D slider to the renderer.

        Returns:
            The added 3D slider object.
        """
        return self.renderer.add_slider3d(*args, **kwargs)
    
    def remove(self, name):
        """Remove an object from the renderer.

        Args:
            name: The name of the object to remove.
        """
        self.renderer.remove(name)

    def clear(self):
        """Clear the renderer."""
        self.renderer.clear()