Auth
====

.. see:: https://vaultproject.io/docs/auth/index.html

Auth backends are the components in Vault that perform authentication and are responsible for assigning identity and a set of policies to a user.

Having multiple auth backends enables you to use an auth backend that makes the sense for your use case of Vault and your organization.

API
---

Enabling and configuring app-id backend::

    APP = 'foo'
    USER = 'bar'
    POLICIES = ['dummy']

    backend = yield from client.auth.enable('app-id')
    yield from backend.write_app(APP, policies=POLICIES)
    yield from backend.write_user(USER, app=APp)

Login with app-id::

    token = yield from client.login('app-id', app=APP, user=BAR)

Enabling and configuring cert backend::

    NAME = 'foo'
    CSR_CERT = open('client.csr').read()
    POLICIES = ['dummy']

    backend = yield from client.auth.enable('cert')
    yield from backend.write_cert(NAME, certificate=CSR_CERT, policies=POLICIES)

Login with cert::

    token = yield from client.login('cert')

Enabling and configuring github backend::

    ORGANIZATION = 'foo'
    TEAM = 'bar'

    backend = yield from client.auth.enable('github')
    yield from backend.configure(organization=ORGANIZATION)
    yield from backend.write_team(TEAM, policies=POLICIES)

Login with github::

    GITHUB_TOKEN = '1234567890'

    token = yield from client.login('github', github_token=GITHUB_TOKEN)

Enabling and configuring ldap backend::

    LDAP_URL = 'ldap://ldap.forumsys.com'
    USER_ATTR = 'uid'
    USER_DN = 'dc=example,dc=com'
    GROUP_DN = 'dc=example,dc=com'
    GROUP_NAME = 'scientists'
    POLICIES = ['foo']

    backend = yield from client.auth.enable('ldap')
    yield from backend.configure(url=LDAP_URL,
                                 userattr=USER_ATTR,
                                 userdn=USER_DN,
                                 groupdn=GROUP_DN)
    yield from backend.write_group(name=GROUP_NAME, policies=POLICIES)

Login with ldap::

    USER = 'tesla'
    PASSWORD = 'password'

    token = yield from client.login('ldap', username=USER, password=PASSWORD)

Enabling and configuring userpass backend::

    USER = 'mitchellh'
    PASSWORD = 'foo'

    backend = yield from client.auth.enable('userpass')
    yield from backend.create('mitchellh', 'foo')

Login with userpass::

    token = yield from client.auth.login('userpass',
                                         username=USER,
                                         password=PASSWORD)


Internals
---------

.. autoclass:: aiovault.v1.AuthEndpoint
   :members:
   :inherited-members:


Backends
--------

.. autoclass:: aiovault.v1.auth.backends.AppIDBackend
   :members:
   :inherited-members:

.. autoclass:: aiovault.v1.auth.backends.CertBackend
   :members:
   :inherited-members:

.. autoclass:: aiovault.v1.auth.backends.GitHubBackend
   :members:
   :inherited-members:

.. autoclass:: aiovault.v1.auth.backends.LDAPBackend
   :members:
   :inherited-members:

.. autoclass:: aiovault.v1.auth.backends.UserPassBackend
   :members:
   :inherited-members:


Objects
-------

.. autoclass:: aiovault.LoginToken
   :members:

.. autoclass:: aiovault.ReadToken
   :members:
