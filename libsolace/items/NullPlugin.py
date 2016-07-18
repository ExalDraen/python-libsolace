from libsolace import Plugin
import libsolace

@libsolace.plugin_registry.register
class NullPlugin(Plugin):
    plugin_name = "NullPlugin"
    args = None
    kwargs = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def some_method(self, *args, **kwargs):
        return args, kwargs

    def some_kwarg_method(self, *args, **kwargs):
        return kwargs[0]
