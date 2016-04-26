#!/usr/bin/env python

"""
Goes through the necessary to generate a markdown file of all the doc strings
"""

import logging
from collections import OrderedDict

import libsolace.settingsloader as settings
import libsolace
import libsolace.Decorators as Decorators
import libsolace.Naming as Naming
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceProvision import SolaceProvision
from libsolace.plugin import Plugin
import re

from libsolace.SolaceXMLBuilder import SolaceXMLBuilder

pattern = "(__[a-zA-Z0-9_]*(__)?)"
public_methods = re.compile(pattern)


classes_list = libsolace.plugin_registry.plugins_dict

classes_list['SolaceXMLBuilder'] = SolaceXMLBuilder().__class__
classes_list['Decorators'] = Decorators
classes_list['Plugin'] = Plugin().__class__
classes_list['Naming'] = Naming
classes_list['SolaceCommandQueue'] = SolaceCommandQueue().__class__
classes_list['SolaceProvision'] = SolaceProvision().__class__

ignore_list = [
    "Decorators.MissingClientUser",
    "Decorators.MissingException",
    "Decorators.get_calling_module",
    "Decorators.wraps"
]

logging.info(classes_list)


def get_callable_methods(clazz):
    """
    Returns methods that can be called and are not private

    :param clazz:
    :return:
    """
    methods = []
    for method in dir(clazz):
        if callable(getattr(clazz, method)):
            if not public_methods.match(method):
                methods.append(method)
    return methods


print("# libsolace")
print(libsolace.__doc__)

print("Table of Contents\n=================\n\n")

for plugin in classes_list:
    print("* [%s](#%s)" % (plugin, plugin.lower()))
    # clazz = libsolace.plugin_registry(plugin, setting=settings)
    clazz = classes_list[plugin]
    plugin_name = getattr(clazz, "plugin_name", plugin).lower()
    for method in get_callable_methods(clazz):
        name = "%s%s" % (plugin_name, method)
        logging.info("Toc Item: %s" % name)
        if name not in ignore_list:
            print("   * [%s](#%s)" % (method, name.lower()))

# classes

for plugin in classes_list:
    logging.info("Plugin: %s" % plugin)
    clazz = classes_list[plugin]
    plugin_name = getattr(clazz, "plugin_name", plugin)
    print("\n## %s" % plugin_name)
    print(clazz.__doc__)

    for method in get_callable_methods(clazz):
        name = "%s.%s" % (plugin_name, method)
        if name not in ignore_list:
            print("\n### %s" % name)
            if getattr(clazz, method).__doc__ is not None:
                print("\n%s" % getattr(clazz, method).__doc__)
            else:
                print("Document me!")
