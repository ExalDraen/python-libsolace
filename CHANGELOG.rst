Change Log
==========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_ and this project adheres to
`Semantic Versioning`_.

`Unreleased`_
-------------

Added
~~~~~

-  Nothing

Changed
~~~~~~~

-  Nothing

`0.3.0`_
-------------

Added
~~~~~

-  Added `settings_override` parameter to `SolaceAPI` to allow for overriding of settings
   from `libsolace.yaml`

Changed
~~~~~~~

-  Small PEP8 formatting refactoring
-  Clean up the way settings are loaded from disk.
-  Changed logging: we now no longer configure the root logger and default handler. Instead
   each module has its own logger that has a `NullHandler` attached. This allows
   library users to attach their own handlers and individually configure logging.

`0.2.3` - 2018-12-15
---------------------

Added
~~~~~

-  Added travis CI for releasing new versions to PyPI

Changed
~~~~~~~

- Downgrade "only one appliance in config" log to `INFO` from `WARN`

`0.2.2` - 2018-11-01
---------------------

Changed
~~~~~~~

-  If we do not have XSD files for a given SolOS version, now fall back to
   When validating schema, fall back to latest Sol schema (7.1.1). Also, use
   `6.2` schema for version `6.1` since we don't have access to the 6.1 schema.

`0.2.1` - 2018-10-26
----------------------
First repackaged version of https://github.com/unixunion/python-libsolace uploaded to PyPI

Added
~~~~~

-  PyPI package

Changed
~~~~~~~

- Dropped support for Python <2.6.

Changed
~~~~~~~

-  Nothing

.. _Unreleased: https://github.com/ExalDraen/python-libsolace/compare/0.2.3...master
.. _0.3.0: https://github.com/ExalDraen/python-libsolace/compare/0.2.3...0.3.0
.. _Keep a Changelog: http://keepachangelog.com/
.. _Semantic Versioning: http://semver.org/
