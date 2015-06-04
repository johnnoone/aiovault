import asyncio
import configparser
import json
import logging
import os
import os.path
import pytest
import re
import sys
from collections.abc import Mapping
from functools import wraps
from subprocess import Popen, PIPE
from time import sleep

__tracebackhide__ = True

HERE = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def async_test(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # __tracebackhide__ = True

        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
        pending = asyncio.Task.all_tasks()
        if pending:
            loop.run_until_complete(asyncio.wait(pending))
    return wrapper


def extract(src, pattern):
    try:
        return re.search(pattern, src).group(1)
    except AttributeError:
        pass


class Vault:

    def __init__(self, name):
        self.name = name
        self._proc = None
        self._data = None

    @property
    def config(self):
        return self._data

    def start(self):
        if self._proc:
            raise Exception('Vault %s is already running' % self.name)

        env = os.environ.copy()
        env.setdefault('GOMAXPROCS', '2')

        clean = Popen(['killall', 'vault'],
                      stdout=PIPE,
                      stderr=PIPE,
                      env=env,
                      shell=False)
        clean.communicate()

        args = ['vault', 'server', '-dev']

        proc = Popen(args, stdout=PIPE, stderr=PIPE, env=env, shell=False)
        self._proc = proc

        logging.info('Starting %s [%s]' % (self.name, proc.pid))

        buf = ''
        while 'Vault server started!' not in buf:
            buf += proc.stdout.read(1).decode('utf-8')

        logging.debug(buf)

        data = {
            'addr': extract(buf, 'VAULT_ADDR=\'(.+)\''),
            'unseal_key': extract(buf, 'Unseal Key: ([\w-]+)\W'),
            'root_token': extract(buf, 'Root Token: ([\w-]+)'),
        }

        env.setdefault('VAULT_ADDR', data['addr'])
        proc_kwargs = {'stdout': PIPE,
                       'stderr': PIPE,
                       'env': env,
                       'shell': False}
        for i in range(60):
            with Popen(['vault', 'status'], **proc_kwargs) as sub:
                stdout, stderr = sub.communicate(timeout=5)
                if sub.returncode in (0, 1):
                    buf = stdout.decode('utf-8')
                    break
            sleep(1)
        else:
            raise Exception('Unable to start %s [%s]' % (self.name, proc.pid))

        data.update({
            'sealed': extract(buf, 'Sealed: (\w+)') == 'true',
            'shares': int(extract(buf, 'Key Shares: (\d+)')),
            'threshold': int(extract(buf, 'Key Threshold: (\d+)')),
            'progress': int(extract(buf, 'Unseal Progress: (\d+)')),
            'ha': extract(buf, 'High-Availability Enabled: (\w+)') == 'true',
        })

        self._data = Namespace()
        self._data.update(data)
        logging.info('Vault %s [%s] is ready to rock %s',
                     self.name,
                     proc.pid,
                     data)

    def stop(self):
        if not self._proc:
            raise Exception('Node %s is not running' % self.name)
        logging.info('Halt %s [%s]' % (self.name, self._proc.pid))
        result = self._proc.terminate()
        self._proc = None
        return result

    def __repr__(self):
        return '<Vault(name=%r)>' % self.name


class VaultTLS:
    def __init__(self, name, *, server_config):
        self.name = name
        self._proc = None
        self._data = None
        self.server_config = server_config

    @property
    def config(self):
        return self._data

    def start(self):
        if self._proc:
            raise Exception('Vault %s is already running' % self.name)

        env = os.environ.copy()
        env.setdefault('GOMAXPROCS', '2')
        # env['SSL_CERT_DIR'] = os.path.join(HERE, 'certs')

        clean = Popen(['killall', 'vault'],
                      stdout=PIPE, stderr=PIPE, env=env, shell=False)
        clean.communicate()
        cwd = os.path.dirname(self.server_config)
        args = ['vault', 'server', '-config', self.server_config]

        proc = Popen(args,
                     stdout=PIPE,
                     stderr=PIPE,
                     env=env,
                     shell=False,
                     cwd=cwd)
        self._proc = proc

        logging.info('Starting %s [%s]' % (self.name, proc.pid))

        buf = ''
        while 'Vault server started!' not in buf:
            buf += proc.stdout.read(1).decode('utf-8')

        logging.debug(buf)

        with open(self.server_config) as file:
            configuration = json.load(file)['listener']['tcp']
            if configuration.get('tls_disable', False):
                addr = 'http://%s' % configuration['address']
            else:
                addr = 'https://%s' % configuration['address']
            base = os.path.dirname(self.server_config)
            data = {
                'addr': addr,
                'key': os.path.join(base, 'server.key'),
                'crt': os.path.join(base, 'server.crt'),
                'csr': os.path.join(base, 'server.csr'),
            }

        # env.setdefault('VAULT_ADDR', data['addr'])
        self._data = Namespace()
        self._data.update(data)
        logging.info('Vault %s [%s] is ready to rock %s',
                     self.name,
                     proc.pid,
                     data)

    def stop(self):
        if not self._proc:
            raise Exception('Node %s is not running' % self.name)
        logging.info('Halt %s [%s]' % (self.name, self._proc.pid))
        result = self._proc.terminate()
        self._proc = None
        return result

    def __repr__(self):
        return '<Vault(name=%r, server_config=%r)>' % (self.name,
                                                       self.server_config)


class Consul(object):
    def __init__(self, name, config_file, server=False, leader=False):
        self.name = name
        self.config_file = config_file
        self.server = server
        self.leader = leader
        self._proc = None

    @property
    def config(self):
        with open(self.config_file) as file:
            response = Namespace()
            response.update({'address': '127.0.0.1:8500'})
            response.update(json.load(file))
            return response

    def start(self):
        if self._proc:
            raise Exception('Node %s is already running' % self.name)

        # reset tmp store
        Popen(['rm', '-rf', self.config.data_dir]).communicate()

        env = os.environ.copy()
        env.setdefault('GOMAXPROCS', '2')
        proc = Popen(['consul', 'agent', '-config-file=%s' % self.config_file],
                     stdout=PIPE, stderr=PIPE, env=env, shell=False)
        self._proc = proc
        logging.info('Starting %s [%s]' % (self.name, proc.pid))
        for i in range(60):
            with Popen(['consul', 'info'], stdout=PIPE, stderr=PIPE) as sub:
                stdout, stderr = sub.communicate(timeout=5)
                if self.leader:
                    if 'leader = true' in stdout.decode('utf-8'):
                        break
                elif self.server:
                    if 'server = true' in stdout.decode('utf-8'):
                        break
                elif not sub.returncode:
                    break
            sleep(1)
        else:
            raise Exception('Unable to start %s [%s]' % (self.name, proc.pid))
        logging.info('Node %s [%s] is ready to rock' % (self.name, proc.pid))

    def stop(self):
        if not self._proc:
            raise Exception('Node %s is not running' % self.name)
        logging.info('Halt %s [%s]' % (self.name, self._proc.pid))
        result = self._proc.terminate()
        self._proc = None
        return result


@pytest.fixture(scope='function', autouse=False)
def consul(request):
    config_file = os.path.join(HERE, 'consul-server.json')
    server = Consul('leader', config_file, True, True)
    server.start()
    request.addfinalizer(server.stop)
    return server.config


@pytest.fixture(scope='function', autouse=False)
def dev_server(request):
    server = Vault('dev')
    server.start()
    request.addfinalizer(server.stop)
    return server.config


@pytest.fixture(scope='function', autouse=False)
def server(request):
    conf = os.path.join(HERE, 'certs/server.json')
    server = VaultTLS('https', server_config=conf)
    server.start()
    request.addfinalizer(server.stop)
    return server.config


@pytest.fixture(scope='session', autouse=True)
def env(request):
    response = Namespace()
    response.update(os.environ)
    response.CERT_PATH = os.path.join(HERE, 'certs')

    config = configparser.ConfigParser()
    config.optionxform = str  # disable case transformation
    config.read(['vault-test.ini', os.path.expanduser('~/.vault-test.ini')])
    if config.has_section('env'):
        response.update(config.items('env'))
    return response


class Namespace:

    def update(self, data):
        if isinstance(data, Mapping):
            data = data.items()
        for k, v in data:
            setattr(self, k, v)
