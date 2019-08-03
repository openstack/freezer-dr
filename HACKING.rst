Freezer DR Style Commandments
=============================

- Step 1: Read the OpenStack Style Commandments
  https://docs.openstack.org/hacking/latest/
- Step 2: Read on

Freezer DR Specific Commandments
--------------------------------

Logging
-------

Use the common logging module, and ensure you ``getLogger``::

    from oslo_log import log

    LOG = log.getLogger(__name__)

    LOG.debug('Foobar')



Properly Calling Callables
--------------------------

Methods, functions and classes can specify optional parameters (with default
values) using Python's keyword arg syntax. When providing a value to such a
callable we prefer that the call also uses keyword arg syntax. For example::

    def f(required, optional=None):
        pass

    # GOOD
    f(0, optional=True)

    # BAD
    f(0, True)

This gives us the flexibility to re-order arguments and more importantly
to add new required arguments. It's also more explicit and easier to read.
