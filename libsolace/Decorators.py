import logging
from libsolace.util import get_calling_module

def only_on_shutdown(entity):
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            mode = kwargs.get('shutdown_on_apply', None)
            if entity == 'queue' and mode in ['b', 'q', True]:
                return f(*args, **kwargs)
            if entity == 'user' and mode in ['b', 'u', True]:
                return f(*args, **kwargs)
            module = get_calling_module()
            logging.info("Calling package %s - Shutdown on apply is not enabled, bypassing %s for entity %s" % (module, f.__name__, entity))
        return wrapped_f
    return wrap
