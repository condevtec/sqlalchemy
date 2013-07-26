"""Public API functions for the event system.

"""
from __future__ import absolute_import

from .. import util, exc
from .base import _registrars
from .registry import _EventKey

CANCEL = util.symbol('CANCEL')
NO_RETVAL = util.symbol('NO_RETVAL')


def listen(target, identifier, fn, *args, **kw):
    """Register a listener function for the given target.

    e.g.::

        from sqlalchemy import event
        from sqlalchemy.schema import UniqueConstraint

        def unique_constraint_name(const, table):
            const.name = "uq_%s_%s" % (
                table.name,
                list(const.columns)[0].name
            )
        event.listen(
                UniqueConstraint,
                "after_parent_attach",
                unique_constraint_name)

    """

    for evt_cls in _registrars[identifier]:
        tgt = evt_cls._accept_with(target)
        if tgt is not None:
            _EventKey(target, identifier, fn, tgt).listen(*args, **kw)
            break
    else:
        raise exc.InvalidRequestError("No such event '%s' for target '%s'" %
                                (identifier, target))


def listens_for(target, identifier, *args, **kw):
    """Decorate a function as a listener for the given target + identifier.

    e.g.::

        from sqlalchemy import event
        from sqlalchemy.schema import UniqueConstraint

        @event.listens_for(UniqueConstraint, "after_parent_attach")
        def unique_constraint_name(const, table):
            const.name = "uq_%s_%s" % (
                table.name,
                list(const.columns)[0].name
            )
    """
    def decorate(fn):
        listen(target, identifier, fn, *args, **kw)
        return fn
    return decorate


def remove(target, identifier, fn):
    """Remove an event listener.

    The arguments here should match exactly those which were sent to
    :func:`.listen`; all the event registration which proceeded as a result
    of this call will be reverted by calling :func:`.remove` with the same
    arguments.

    e.g.::

        # if a function was registered like this...
        @event.listens_for(SomeMappedClass, "before_insert", propagate=True)
        def my_listener_function(*arg):
            pass

        # ... it's removed like this
        event.remove(SomeMappedClass, "before_insert", my_listener_function)

    Above, the listener function associated with ``SomeMappedClass`` was also
    propagated to subclasses of ``SomeMappedClass``; the :func:`.remove` function
    will revert all of these operations.

    .. versionadded:: 0.9.0

    """
    for evt_cls in _registrars[identifier]:
        tgt = evt_cls._accept_with(target)
        if tgt is not None:
            _EventKey(target, identifier, fn, tgt).remove()
            break
    else:
        raise exc.InvalidRequestError("No such event '%s' for target '%s'" %
                                (identifier, target))


