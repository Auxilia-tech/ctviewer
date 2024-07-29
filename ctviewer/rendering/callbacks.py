class RendererCallbacks:
    def __init__(self, renderer):
        self.renderer = renderer
    
    def add(self, obj):
        self.renderer.add(obj)

    def background(self):
        return self.renderer.background()

    def render(self):
        self.renderer.render()

    def add_slider(self, *args, **kwargs):
        return self.renderer.add_slider(*args, **kwargs)

    def add_slider3d(self, *args, **kwargs):
        return self.renderer.add_slider3d(*args, **kwargs)
    
    def remove(self, name):
        self.renderer.remove(name)

    def clear(self):
        self.renderer.clear()