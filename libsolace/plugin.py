"""
The plugin architecture
"""

import logging
import re

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
        logging.debug("Plugin Init")
        pass

    def register(self, object_class, *args, **kwargs):
        """
        Registers a object with the plugin registry

        :param object_class: object to register, should be a class
        :return:
        """

        logging.info("Registering Plugin: %s from class: %s " % (object_class.plugin_name, object_class) )

        # # TODO FIXME constructor kwargs and args if needed.
        # for name in dir(object_class):
        #   if name.startswith('complete_'):
        #     # completion function required a little more renaming magic
        #     new_name = 'complete_%s_%s' % (object_class.plugin_name, re.sub('complete_', '' ,name))
        #     logging.debug("registering alias for %s as: %s" % (name, new_name))
        #     new_handler = self._make_cmd(object_class, name)
        #     setattr(object_class, new_name, new_handler)
        #     setattr(new_handler, '__doc__', getattr(object_class, name).__doc__)
        #   if not name.startswith('_'):
        #     # every other method that is not private gets an alias
        #     new_name = '%s_%s' % (object_class.plugin_name, name) # eg: verify_pools -> lb_verify_pools
        #     logging.debug("registering alias for %s as: %s" % (name, new_name))
        #     new_handler = self._make_cmd(object_class, name)
        #     setattr(object_class, new_name, new_handler)
        #     setattr(new_handler, '__doc__', getattr(object_class, name).__doc__)

        self.plugins.append(object_class(*args, **kwargs))
        self.plugins_dict[object_class.plugin_name] = object_class(*args, **kwargs)

    # @staticmethod
    # def _make_cmd(plugin, name):
    #   def handler(self, *args, **kwargs):
    #     logging.debug("handler for %s and func %s. self: %s" % (plugin, name, self))
    #     # return the function matching the requested name from self
    #     return getattr(self, name, None)(*args, **kwargs)
    #   return handler


    def __call__(self, *args, **kwargs):
        """
        When you call this with the name of a plugin eg: 'PipelineClientPlugin', this returns the instance
        from the plugin_registry. You might need to call sub methods on that to get it into the state you need,
        for example the reconfigure(settings) method in PipelineClientPlugin.

        :param args: name of Plugin to return
        :param kwargs:
        :return: object
        """
        logging.debug("retrieving %s, %s, %s" % (self, args, kwargs))
        return self.plugins_dict[args[0]]
