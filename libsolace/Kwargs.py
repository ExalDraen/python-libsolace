__author__ = 'keghol'

__doc__ = """
This file is just a documentation holder for various kwargs. No function other than that. Link to items here with epydoc
e.g. @keyword shutdown_on_apply: :func:`shutdown_on_apply`
"""


shutdown_on_apply = None
"""
The shutdown_on_apply kwarg is typically passed in from the CLI for a particular provision task. It can be set to
either a boolean or a char.
- true: shutdown all object types while applying changes
- false: dont shutdown anything
- 'b': shutdown both queues and users while applying changes
- 'q': shutdown only queues while applying changes
- 'u': shutdown only users while applying changes

"""


version = None
"""
Overrides the detected version of the SolOS-TR SEMP request language level. By default, libsolace connects to the
appliances and does a "show version" in order to set the appriate language level. This can fail sometimes as with
the VMR due to the fact that we need a SEMP version to initiate communication with the appliance. If you know your
appliance SolOS-TR version, you can set it manually with this kwargs while instantiating the SolaceAPI instance.

Example:
    >>> api = SolaceAPI("dev", version="soltr/7_1_1")

"""


force = None
"""
A general purpose `force` things boolean. Generally this is used by tests. When passed it bypasses many of the
:class:`libsolace.Decorators` that require preconditions.
"""


primaryOnly = None
"""
Not really a "only" flag, it adds the "primary" node to the "appliances to call" list
"""

backupOnly = None
"""
Not really a "only" flag, it adds the "backup" node to the "appliances to call" list
"""