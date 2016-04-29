import sys

import unittest2 as unittest
from types import MethodType

import libsolace.settingsloader as settings
from libsolace.plugin import PluginResponse
from libsolace.util import *

import yaml


def get_test_logger():
    import logging
    logging.basicConfig(format='%(filename)s:%(lineno)s %(levelname)s %(message)s', stream=sys.stdout)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger().setLevel(logging.INFO)
    return logging


class TestUtil(unittest.TestCase):
    def test_version_equal_or_greater_than(self):
        self.assertTrue(version_equal_or_greater_than('soltr/6_0', 'soltr/7_0'))
        self.assertTrue(version_equal_or_greater_than('soltr/6_0', 'soltr/6_0'))
        self.assertFalse(version_equal_or_greater_than('soltr/7_1_1', 'soltr/6_2'))
        self.assertFalse(version_equal_or_greater_than('soltr/7_1', 'soltr/6_2'))
        with self.assertRaisesRegexp(Exception, "Failed to parse version 6_2") as cm:
            version_equal_or_greater_than('6_2', 'soltr/7_0')


class PrePostCaller:
    def __init__(self, other, api):
        self.other = other
        self.api = api

    def pre(self, func, *args, **kwargs):
        if settings.UPDATE_MOCK_TESTS:
            logging.info('pre func: %s, args: %s kwargs: %s' % (func, args, kwargs))

    def post(self, request, *args, **kwargs):
        if settings.UPDATE_MOCK_TESTS:
            logging.info('post result: %s, args: %s kwargs: %s' % (request, args, kwargs))
            if isinstance(request, PluginResponse):
                logger.info("Dumping Plugin Request %s: %s" % (request.xml, request.kwargs))
                response = self.api.rpc(request, xml_response=True)
                logger.info("Dumping Response: %s" % yaml.dump(response, default_flow_style=False))

    def __getattr__(self, name):
        if hasattr(self.other, name):
            func = getattr(self.other, name)
            if callable(func):
                return lambda *args, **kwargs: self._wrap(func, args, kwargs)
            else:
                return func
        logger.warn("Unable to find attribute: %s in %s" % (name, self.other))
        raise AttributeError(name)

    def _wrap(self, func, args, kwargs):
        self.pre(func, *args, **kwargs)
        if type(func) == MethodType:
            result = func(*args, **kwargs)
        else:
            result = func(self.other, *args, **kwargs)
        self.post(result, *args, **kwargs)
        return result


def get_plugin_from_api(api, plugin_name, **kwargs):
    plugin = PrePostCaller(api.manage(plugin_name, **kwargs), api=api)
    return plugin
