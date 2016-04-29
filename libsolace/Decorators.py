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
    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            module = get_calling_module()
            logging.warning("Deprecation Warning: %s: %s %s" % (warning_msg, module, f.__name__))
            return f(*args, **kwargs)

        return wrapped_f

    return wrap


def before(method_name):
    """Call a named method before the decorated method. This is typically used to tell a object to shutdown so some
    modification can be made.

    Example:

    >>> def shutdown(self, **kwargs):
    >>>    # shutdown some object
    >>> @before("shutdown")
    >>> def delete(self, **kwargs):
    >>>    # delete object since its shutdown

    @parameter method_name: the method name to call
    @type parameter: str
    @keyword skip_before: skips the before hook
    @type skip_before: bool
    @returns: the method
    @rtype: obj

    """

    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):

            # force kwarg, just return the method to allow exec
            if "skip_before" in kwargs:
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


def only_on_shutdown(entity):
    """Only calls the method if the shutdown byte permits it. The entity is one of `queue` or `user` and both have
    differnent trigger scenarios and commons ones too..

        :param entity: (str) "queue" or "user"
        :return: method

    #### User:
    If shutdown is True | b | u for a "user" entity, then allow the method to run.

    #### Queue:
    If shutdown is True | b | q for a "queue" entity, then allow the method to run.

    methods decorated with this can optionally be decorated with the @shutdown decorator if you are needing to
    shutdown the object at the same time. If the object is not shutdown, the appliance will throw a error.

    Example:

    >>> @only_on_shutdown('user')
    >>> def delete_user(**kwargs):
    >>>    return True
    >>> delete_user(shutdown_on_apply='u')
    True
    >>> delete_user(shutdown_on_apply='q')
    None

    """

    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):

            # force kwarg, just return the method to allow exec
            if "force" in kwargs:
                if kwargs["force"]:
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


def only_if_not_exists(entity, data_path, primaryOnly=False, backupOnly=False):
    """Return method if the item does NOT exist in the Solace appliance, setting the kwarg for which appliance needs
    the method run.

    :param entity: the "getter" to call
    :param data_path: a dot name spaced string which will be used to descend into the response document to verify exist
    :param primaryOnly: run the "getter" only against primary
    :param backupOnly: run the "getter" only against backup
    :return: method

    if the object's exists caching bit is False, return the method
    If the object does not exist, return the method and set the exists bit to False
    If the object exists in the appliance, set the exists bit to True

    Example

    >>> @only_if_not_exists('get', 'rpc-reply.rpc.show.client-username.client-usernames.client-username')
    >>> def create_user(**kwargs):
    >>>    return True
    >>> create_user()

    """

    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):

            logging.info(kwargs)

            # force kwarg, just return the method to allow exec
            if "force" in kwargs:
                if kwargs["force"]:
                    args[0].set_exists(True)
                    return f(*args, **kwargs)

            # default false
            check_primary = False
            check_backup = False

            # extract package name
            module = get_calling_module()

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


def only_if_exists(entity, data_path, primaryOnly=False, backupOnly=False):
    """ Return method only if item exists.

    :param entity: the "getter" to call
    :param data_path: a dot name spaced string which will be used to decend into the response document to verify exist
    :param primaryOnly: run the "getter" only against primary
    :param backupOnly: run the "getter" only against backup
    :return: method

If object exists bit set, return the method
If object exists bit not set, query the object, return the method if succes
If object does not exist, dont return the method.

For Example see only_if_not_exists

    """

    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):

            # default false
            check_primary = False
            check_backup = False

            # extract package name
            module = get_calling_module()

            # force kwarg, just return the method to allow exec
            if "force" in kwargs:
                if kwargs["force"]:
                    args[0].set_exists(True)
                    return f(*args, **kwargs)

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
    """ Sets the primaryOnly kwarg before calling the method. Use this to force a method onto a specific router.
Note, this does NOT unset backupOnly kwarg, so you can actualy double target.

    :return: method
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
    """ Sets the backupOnly kwarg before calling the method. Use this to force a method onto a specific router.
Note, this does NOT unset primaryOnly kwarg, so you can actualy double target.

    :return: method
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
