#!/usr/bin/env python

"""
Goes through the neccessary to generate a markdown file of all the doc strings
"""

import logging
import libsolace.settingsloader as settings
import libsolace
import re

pattern = "(__[a-zA-Z0-9_]*(__)?)"
public_methods = re.compile(pattern)

classes_list = libsolace.plugin_registry.plugins_dict


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


print("Table of Contents\n=================\n\n")

for plugin in classes_list:
    print("* [%s](#%s)" % (plugin, plugin.lower()))
    clazz = libsolace.plugin_registry(plugin, setting=settings)
    for method in get_callable_methods(clazz):
        print("   * [%s](#%s%s)" % (method, clazz.plugin_name.lower(), method.lower()))


# classes

for plugin in classes_list:
    logging.info("Plugin: %s" % plugin)
    clazz = libsolace.plugin_registry(plugin, setting=settings)
    print("\n## %s" % clazz.plugin_name)
    print(clazz.__doc__)

    for method in get_callable_methods(clazz):
        print("\n### %s.%s" % (clazz.plugin_name, method))
        if getattr(clazz, method).__doc__ is not None:
            print("\n%s" % getattr(clazz, method).__doc__)
        else:
            print("Document me!")

