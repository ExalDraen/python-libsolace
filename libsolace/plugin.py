"""
The plugin architecture
"""

import logging


from libsolace.util import get_calling_module


class PluginClass(type):
    """
    This is a metaclass for construction only.
    """

    def __new__(cls, clsname, bases, dct):
        new_object = super(PluginClass, cls).__new__(cls, clsname, bases, dct)
        return new_object


class Plugin(object):
    """
    This is the plugin core object where all pluggables should extend from and register too.

    Example:

    import pprint
    import libsolace
    from libsolace.plugin import Plugin
    # Startup the plugin system
    libsolace.plugin_registry = Plugin()


    @libsolace.plugin_registry.register
    class Bar(Plugin):
        # must have a name for the plugin, helps calling it by name later.
        plugin_name = "BarPlugin"

        # Instance methods work!
        def hello(self, name):
            print("Hello %s from %s" % (name, self))

        # Static methods work too!
        @staticmethod
        def gbye():
            print("Cheers!")


    libsolace.plugin_registry('BarPlugin').hello("dude")
    libsolace.plugin_registry('BarPlugin').gbye()
    pprint.pprint(dir(libsolace.plugin_registry('BarPlugin')))


    """
    __metaclass__ = PluginClass
    plugins = []
    plugins_dict = {}
    plugin_name = None

    def __init__(self, *args, **kwargs):
        logging.debug("Plugin Init: %s, %s" % (args, kwargs))

    def register(self, object_class, *args, **kwargs):
        """Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        """
        logging.info("Registering Plugin id: %s from: %s " % (object_class.plugin_name, object_class))
        # o = object_class(*args, **kwargs)
        o = object_class
        self.plugins.append(o)
        self.plugins_dict[object_class.plugin_name] = o

    def __call__(self, *args, **kwargs):
        """
        When you call this with the name of a plugin eg: 'PipelineClientPlugin', this returns the class
        from the plugin_registry. You might need to call sub methods on that to get it into the state you need,
        for example the reconfigure(settings) method in PipelineClientPlugin.

        :param args: name of Plugin to return
        :param kwargs:
        :return: class
        """

        module = get_calling_module(point=2)

        logging.debug(self.plugins_dict)
        logging.info("Module %s Requesting Plugin %s" % (module, args[0]))
        logging.debug("Plugin Request: args: %s, kwargs: %s" % (args, kwargs))
        try:
            # logging.info("Class: %s" % self.plugins_dict[args[0]].__class__)
            # return self.plugins_dict[args[0]].__class__
            logging.debug("Class: %s" % self.plugins_dict[args[0]])
            return self.plugins_dict[args[0]]
        except:
            logging.warn("No plugin named: %s found, available plugins are: %s" % (args[0], self.plugins_dict))
            logging.warn(
                "Please check the plugin is listed in the yaml config and that you have @libsolace.plugin_registry.register in the class")
            raise

    def set_exists(self, state):
        """Exists bool is used to cut down on using SEMP queries to validate existence of items.


    :param state: exists or not boolean
    :type state: bool
    :return:
        """
        module = get_calling_module(point=3)
        logging.info("Calling module: %s, Setting Exists bit: %s" % (module, state))
        self.exists = state
