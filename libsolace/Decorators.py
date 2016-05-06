import functools
import logging
from functools import wraps

from libsolace.Exceptions import MissingException, MissingClientUser
from libsolace.util import get_calling_module

# plugin_name = "Decorators"

__doc__ = """
Some decorators which are used within the Plugins in order to control / limit execution.
"""


def deprecation_warning(warning_msg):
    """
    Log a deprecation warning and carry on.

    :param warning_msg: the warning text
    :type warning_msg: str
    :rtype: object
    :returns: the decorated object
    """
    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            module = get_calling_module()
            logging.warning("Deprecation Warning: %s: %s %s" % (warning_msg, module, f.__name__))
            return f(*args, **kwargs)

        return wrapped_f

    return wrap


def before(method_name, skip_before=False):
    """
    Call a named method before. This is typically used to tell a object to shutdown so some modification can be made.
    This decorator passes all kwargs and args on to the "before" method so keep your params and keywords in sync!

    Example:

    .. doctest::
        :options: +SKIP

        >>> def shutdown(self, **kwargs):
        >>>    # shutdown some object
        >>> @before("shutdown")
        >>> def delete(self, **kwargs):
        >>>    # delete object since its shutdown

    :param method_name: the method name to call
    :type method_name: str
    :param skip_before: skips the before hook
    :type skip_before: bool
    :returns: the decorated object
    :rtype: obj

    """

    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):

            # force kwarg, just return the method to allow exec
            if kwargs["skip_before"]:
                return f(*args, **kwargs)

            api = getattr(args[0], "api")
            logging.info("calling object %s's shutdown hook" % api)
            try:
                api.rpc(str(getattr(args[0], method_name)(**kwargs)))
                return f(*args, **kwargs)
            except Exception, e:
                raise BaseException(
                    "Error calling @before(%s) method in %s kwargs: %s" % (method_name, args[0], kwargs))

        return wrapped_f

    return wrap


def only_on_shutdown(entity, **kwargs):
    """
    Only calls the method if the shutdown_on_apply rules apply to the `entity` type. The entity can be either `queue` or
    `user`.

    Methods decorated with this can optionally be decorated with the @shutdown decorator to actually call whatever method
    is capable of shutting down the object. If the object is not shutdown correcty, the appliance can not change the property
    and will raise an exception.

    Example:

    .. doctest::
        :options: +SKIP

        >>> @only_on_shutdown('user')
        >>> def delete_user(**kwargs):
        >>>    return True
        >>> delete_user(shutdown_on_apply='u')
        True
        >>> delete_user(shutdown_on_apply='q')
        None

    :param entity: the type of entity were expecting for the following comparisons:

        "user": If shutdown_on_apply is True | b | u for a "user" entity, then allow the method to run.

        "queue": If shutdown_on_apply is True | b | q for a "queue" entity, then allow the method to run.

    :type entity: str
    :param force: :data:`libsolace.Kwargs.force`
    :type force: bool
    :param shutdown_on_apply: :data:`libsolace.Kwargs.shutdown_on_apply`
    :rtype: object
    :returns: the object to call

    """

    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):

            # if force, return the method to allow exec
            if "force" in kwargs and kwargs.get('force'):
                args[0].set_exists(True)
                return f(*args, **kwargs)

            mode = kwargs.get('shutdown_on_apply', None)
            if entity == 'queue' and mode in ['b', 'q', True]:
                return f(*args, **kwargs)
            if entity == 'user' and mode in ['b', 'u', True]:
                return f(*args, **kwargs)
            module = get_calling_module()
            logging.info(
                    "Package %s requires shutdown of this object, shutdown_on_apply is not set for this object type, bypassing %s for entity %s" % (
                        module, f.__name__, entity))

        return wrapped_f

    return wrap


def only_if_not_exists(entity, data_path, primaryOnly=False, backupOnly=False, **kwargs):
    """
    Call the method only if the Solace object does NOT exist in the Solace appliance.

        - if the object's exists caching bit is False, return the method
        - If the object does not exist, return the method and set the exists bit to False
        - If the object exists in the appliance, set the exists bit to True

    Example:

    .. doctest::
        :options: +SKIP

        >>> @only_if_not_exists('get', 'rpc-reply.rpc.show.client-username.client-usernames.client-username')
        >>> def create_user(**kwargs):
        >>>    return True
        >>> create_user()

    :param entity: the "getter" method to call by name
    :type entity: str
    :param data_path: a dot name spaced string which will be used to descend into the response document to verify existence
    :type data_path: str
    :param primaryOnly: :data:`libsolace.Kwargs.primaryOnly`
    :type primaryOnly: bool
    :param backupOnly: :data:`libsolace.Kwargs.backupOnly`
    :type backupOnly: bool
    :param force: :data:`libsolace.Kwargs.force`
    :type force: bool
    :rtype: object
    :returns: the object to call

    """

    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):

            logging.info(kwargs)

            # force kwarg, just return the method to allow exec
            if "force" in kwargs and kwargs.get('force'):
                args[0].set_exists(True)
                return f(*args, **kwargs)

            # default false
            check_primary = False
            check_backup = False

            # extract package name
            module = get_calling_module()

            # force kwarg, just return the method to allow exec
            if "force" in kwargs and kwargs.get('force'):
                logging.info("Force being used, returning obj")
                args[0].set_exists(False)
                return f(*args, **kwargs)
            else:
                logging.info("Not forcing return of object")

            # determine if were checking both or a single node
            if primaryOnly:
                kwargs['primaryOnly'] = primaryOnly
                check_primary = True
            elif backupOnly:
                kwargs['backupOnly'] = backupOnly
                check_backup = True
            else:
                logging.info("Package: %s requests that Both primary and backup be queried" % module)
                check_primary = True
                check_backup = True

            # if exists bit is set on the object ( caching )
            try:
                if not args[0].exists:
                    logging.info("Cache hit, object does NOT exist")
                    return f(*args, **kwargs)
            except Exception, e:
                pass

            logging.debug("Cache miss")

            logging.info("Package: %s, asking entity: %s, for args: %s, kwargs: %s via data_path: %s" % (
                module, entity, str(args), str(kwargs), data_path))

            response_path = data_path.split('.')

            # if the getattr fails with a MissingException, which means our condition is met
            try:
                res = getattr(args[0], entity)(**kwargs)
            except MissingException:
                exists = False
                args[0].set_exists(exists)
                return f(*args, **kwargs)

            logging.info("Response %s" % res)

            # try peek into attributes, any raises means one of the nodes does not have the object.
            o_res = res

            exists = True

            for p in response_path:
                if check_primary:
                    try:
                        res[0] = res[0][p]
                    except (KeyError, TypeError, IndexError):
                        logging.info("Object not found on PRIMARY, key:%s setting primaryOnly" % p)
                        logging.info(o_res)
                        kwargs['primaryOnly'] = True
                        exists = False
                if check_backup:
                    try:
                        res[1] = res[1][p]
                    except (KeyError, TypeError, IndexError):
                        logging.info("Object not found on BACKUP, key:%s setting backupOnly" % p)
                        logging.info(o_res)
                        kwargs['backupOnly'] = True
                        exists = False

            if not exists:
                args[0].set_exists(exists)
                return f(*args, **kwargs)
            else:
                # if we reach here, the object exists
                logging.info(
                        "Package %s - %s, the requested object already exists, ignoring creation" % (
                            module, f.__name__))
                args[0].set_exists(exists)

        return wrapped_f

    return wrap


def only_if_exists(entity, data_path, primaryOnly=False, backupOnly=False, **kwargs):
    """ The inverse of :func:`only_if_not_exists` """

    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):

            # default false
            check_primary = False
            check_backup = False

            # extract package name
            module = get_calling_module()

            # force kwarg, just return the method to allow exec
            if "force" in kwargs and kwargs.get('force'):
                logging.info("Force being used, returning obj")
                args[0].set_exists(True)
                return f(*args, **kwargs)
            else:
                logging.info("Not forcing return of object")

            # determine if were checking both or a single node
            if primaryOnly:
                kwargs['primaryOnly'] = primaryOnly
                check_primary = True
            elif backupOnly:
                kwargs['backupOnly'] = backupOnly
                check_backup = True
            else:
                logging.info("Package: %s requests that Both primary and backup be queried" % module)
                check_primary = True
                check_backup = True

            # if exists bit is set on the object ( caching )
            try:
                if args[0].exists:
                    logging.info("Cache hit, object exists")
                    return f(*args, **kwargs)
            except Exception, e:
                pass

            logging.debug("Cache miss")
            logging.info("Package: %s, asking entity: %s, for args: %s, kwargs: %s via data_path: %s" % (
                module, entity, str(args), str(kwargs), data_path))

            response_path = data_path.split('.')

            res = getattr(args[0], entity)(**kwargs)
            o_res = res
            logging.debug("Response %s" % res)

            exists = True

            # try peek into attributes, any raises means one of the nodes does not have the object.
            for p in response_path:
                if check_primary:
                    try:
                        res[0] = res[0][p]
                    except (TypeError, IndexError):
                        logging.info("Object not found on PRIMARY, key:%s error" % p)
                        logging.info(o_res)
                        kwargs['primaryOnly'] = True
                        args[0].set_exists(False)
                        exists = False
                if check_backup:
                    try:
                        res[1] = res[1][p]
                    except (TypeError, IndexError):
                        logging.info("Object not found on BACKUP, key:%s error" % p)
                        logging.info(o_res)
                        kwargs['backupOnly'] = True
                        args[0].set_exists(False)
                        exists = False

            if exists:
                module = get_calling_module()
                logging.info(
                        "Package %s - the requested object exists, calling method %s, check entity was: %s" % (
                            module, f.__name__, entity))
                args[0].set_exists(True)
                return f(*args, **kwargs)

        return wrapped_f

    return wrap


def primary():
    """
    Sets the primaryOnly kwarg before calling the method. Use this to add a specific router to the appliances to call list.
    Note, this does not unset backupOnly kwarg, so you can actualy double target.

    :returns: method
    """

    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            kwargs['primaryOnly'] = True
            module = get_calling_module()
            logging.info("Calling package %s - Setting primaryOnly: %s" % (module, f.__name__))
            return f(*args, **kwargs)

        return wrapped_f

    return wrap


def backup():
    """
    Sets the backupOnly kwarg before calling the method. Use this to add a specific router to the appliances to call list.
    Note, this does not unset primaryOnly kwarg, so you can actualy double target.

    :returns: method
    """

    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            kwargs['backupOnly'] = True
            module = get_calling_module()
            logging.info("Calling package %s - Setting backupOnly: %s" % (module, f.__name__))
            return f(*args, **kwargs)

        return wrapped_f

    return wrap
