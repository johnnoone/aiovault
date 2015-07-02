Audit
=====


.. see:: https://vaultproject.io/docs/audit/index.html


Audit backends are the components in Vault that keep a detailed log of all requests and response to Vault. Because every operation with Vault is an API request/response, the audit log contains every interaction with Vault, including errors.

Vault ships with multiple audit backends, depending on the location you want the logs sent to. Multiple audit backends can be enabled and Vault will send the audit logs to both. This allows you to not only have a redundant copy, but also a second copy in case the first is tampered with.


API
---

Enabling/Disabling syslog backend::

    yield from client.audit.enable('syslog')
    yield from client.audit.disable('syslog')

Enabling/Disabling file backend::

    yield from client.audit.enable('file', path='/path/to/file')
    yield from client.audit.disable('file')

List enabled backends::

    yield from client.audit.items()


Internals
---------

.. autoclass:: aiovault.v1.AuditEndpoint
   :members:
   :inherited-members:


Backends
--------

.. autoclass:: aiovault.v1.audit.backends.FileBackend
   :members:
   :inherited-members:

.. autoclass:: aiovault.v1.audit.backends.SyslogBackend
   :members:
   :inherited-members:
