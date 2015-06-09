Quickstart
==========

This document will try to present the most of the AIOVault's feature in on place.


Initializing the Server
-----------------------

::

    from aiovault import Vault

    root = Vault()
    initial_state = yield from root.initialize()

Keep the initial_state! It is where the root and seal are stored::

    yield from root.seal.unseal(initial_state)

And voila, you server is initialized


Enabling audit backends
-----------------------

::

    yield from root.audit.enable('file', path='/tmp/aiovault.log')


Configuring auth backends
-------------------------

The process is still the same, as root, enable and configure backend.
For example, the ``app-id`` backend::

    APP = 'foo'
    USER = 'BAR'

    # on the server side
    backend = yield from root.auth.enable('app-id')
    yield from backend.write_app(APP, policies=['dummy'])
    yield from backend.write_user(USER, app=APP)

And then, on the client side, you will be able to login with these new
credentials::

    # on the client side
    client = Vault()
    backend = client.auth.load('app-id')
    result = yield from backend.login(app=APP, user=USER)


Configuring secret backends
---------------------------

::

    KEY = 'foo'
    PLAIN_TEXT = 'My taylor is rich'

    created, backend = yield from root.secret.mount('transit')
    yield from backend.write_key(KEY)
    encrypted = yield from backend.encrypt(KEY, PLAIN_TEXT)['ciphertext']
