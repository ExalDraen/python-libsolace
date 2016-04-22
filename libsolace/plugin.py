"""
The plugin architecture
"""
import functools
import logging
from collections import OrderedDict

from libsolace.util import get_calling_module


class PluginClass(type):
    """This is a metaclass for construction only, see Plugin rather"""

    def __new__(cls, clsname, bases, dct):
        new_object = super(PluginClass, cls).__new__(cls, clsname, bases, dct)
        return new_object


class Plugin(object):
    """This is the plugin core object where all plugins should extend from and register too.

    Plugin Example:

    >>> import pprint
    >>> import libsolace
    >>> from libsolace.plugin import Plugin
    >>> libsolace.plugin_registry = Plugin()
    >>> @libsolace.plugin_registry.register
    >>> class Bar(Plugin):
    >>>     # must have a name for the plugin, helps calling it by name later.
    >>>     plugin_name = "BarPlugin"
    >>>     # Instance methods work!
    >>>     def hello(self, name):
    >>>         print("Hello %s from %s" % (name, self))
    >>>     # Static methods work too!
    >>>     @staticmethod
    >>>     def gbye():
    >>>         print("Cheers!")
    >>> libsolace.plugin_registry('BarPlugin').hello("dude")
    >>> libsolace.plugin_registry('BarPlugin').gbye()
    >>> pprint.pprint(dir(libsolace.plugin_registry('BarPlugin')))

    Plugin Instantiation:

    >>> import libsolace.settingsloader as settings
    >>> from libsolace.SolaceAPI import SolaceAPI
    >>> api = SolaceAPI("dev")
    >>> api.manage("BarPlugin")

    Direct Instantiation:

    >>> import libsolace.settingsloader as settings
    >>> import libsolace
    >>> my_clazz = libsolace.plugin_registry("BarPlugin", settings=settings)
    >>> my_instance = clazz(settings=settings)

    """
    __metaclass__ = PluginClass
    plugins = []
    plugins_dict = OrderedDict()
    plugin_name = "Plugin"

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
        def _d(fn):
            return functools.update_wrapper(d(fn), fn)
        functools.update_wrapper(_d, object_class)
        return _d

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
        """set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        """
        module = get_calling_module(point=3)
        logging.info("Calling module: %s, Setting Exists bit: %s" % (module, state))
        self.exists = state


class PluginResponse(object):
    def __init__(self, xml, **kwargs):
        """Plugin Response holder
        @param xml: xml string
        @param kwargs: any kwargs
        @rtype: PluginResponse
        @returns: the instance
        """
        self.xml = xml
        self.kwargs = kwargs
