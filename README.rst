AIO Vault
=========


Install
-------

    pip install .


Usage
-----

On the admin side::

    from aiovault import Vault
    client = Vault('127.0.0.1:8200', token=MY_MASTER_TOKEN)

    # mount consul, and policies
    mounted, backend = yield from client.secret.mount('consul')
    yield from backend.config_access('http://127.0.0.1:8500',
                                     token=ACL_MASTER_TOKEN)
    yield from store.write_role('foo', policy=CONSUL_POLICY)

On the client side::

    from aiovault import Vault
    client = Vault('127.0.0.1:8200')

    # login 
    yield from client.auth.login('userpass',
                                 username='mitchellh',
                                 password='foo')
    # generate consul new credential
    credentials = yield from client.secret.load('consul').creds('foo')


Testing
-------

::

    pip install -r requirements-tests.txt --use-mirrors
    py.test  --cov-report html --cov aiovault tests


Setup MySQL with macport
------------------------

Install MySQL::

    sudo port install mysql56-server
    cd /opt/local ; sudo /opt/local/lib/mysql56/bin/mysqld_safe

In another window::

    /opt/local/lib/mysql56/bin/mysqladmin -u root password 'new-password'


Setup postgres with macport
---------------------------

Create db::

    sudo mkdir -p /opt/local/var/db/postgresql94/defaultdb
    sudo chown postgres:postgres /opt/local/var/db/postgresql94/defaultdb
    sudo su postgres -c '/opt/local/lib/postgresql94/bin/initdb -D /opt/local/var/db/postgresql94/defaultdb'


Start server::

    sudo su postgres -c '/opt/local/lib/postgresql94/bin/postgres \
        -D /opt/local/var/db/postgresql94/defaultdb'

or::

    /opt/local/lib/postgresql94/bin/pg_ctl \
        -D /opt/local/var/db/postgresql94/defaultdb -l logfile start
