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

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

HERE = os.path.dirname(os.path.abspath(__file__))


def async_test(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
        pending = asyncio.Task.all_tasks()
        if pending:
            loop.run_until_complete(asyncio.wait(pending))
    return wrapper


def extract(src, pattern):
    return re.search(pattern, src).group(1)


class DevServer:
    def __init__(self, name):
        self.name = name
        self._proc = None
        self._data = None

    @property
    def config(self):
        return self._data

    def start(self):
        if self._proc:
            raise Exception('Node %s is already running' % self.name)

        env = os.environ.copy()
        env.setdefault('GOMAXPROCS', '2')

        clean = Popen(['killall', 'vault'],
                      stdout=PIPE, stderr=PIPE, env=env, shell=False)
        clean.communicate()

        proc = Popen(['vault', 'server', '-dev'],
                     stdout=PIPE, stderr=PIPE, env=env, shell=False)
        self._proc = proc

        print('Starting %s [%s]' % (self.name, proc.pid))

        data = {}
        buf = ''
        while 'Vault server started!' not in buf:
            buf += proc.stdout.read(1).decode('utf-8')

        data = {
            'addr': extract(buf, 'VAULT_ADDR=\'(.+)\''),
            'unseal_key': extract(buf, 'Unseal Key: ([\w-]+)\W'),
            'root_token': extract(buf, 'Root Token: ([\w-]+)'),
        }
        env.setdefault('VAULT_ADDR', data['addr'])
        for i in range(60):
            with Popen(['vault', 'status'], stdout=PIPE, stderr=PIPE, env=env, shell=False) as sub:
                stdout, stderr = sub.communicate(timeout=5)

                if sub.returncode in (0, 1):
                    buf = stdout.decode('utf-8')
                    data.update({
                        'sealed': extract(buf, 'Sealed: (\w+)') == 'true',
                        'shares': int(extract(buf, 'Key Shares: (\d+)')),
                        'threshold': int(extract(buf, 'Key Threshold: (\d+)')),
                        'progress': int(extract(buf, 'Unseal Progress: (\d+)')),
                        'ha': extract(buf, 'High-Availability Enabled: (\w+)') == 'true',
                    })
                    break
            sleep(1)
        else:
            raise Exception('Unable to start %s [%s]' % (self.name, proc.pid))

        self._data = Namespace()
        self._data.update(data)
        print('Node %s [%s] is ready to rock' % (self.name, proc.pid), data)

    def stop(self):
        if not self._proc:
            raise Exception('Node %s is not running' % self.name)
        print('Halt %s [%s]' % (self.name, self._proc.pid))
        result = self._proc.terminate()
        self._proc = None
        return result


@pytest.fixture(scope='function', autouse=False)
def dev_server(request):
    server = DevServer('leader')
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
