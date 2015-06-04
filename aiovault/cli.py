import os
import os.path
import re
from collections import namedtuple
from subprocess import Popen, PIPE


PATTERN_KEYS = re.compile('Key \d+: (?P<key>[a-f0-9]+)')  # noqa
PATTERN_ROOT = re.compile('Initial Root Token: (?P<token>[a-f0-9-]+)')  # noqa
PATTERN_CRITERIAS = re.compile('Vault initialized with (?P<shares>\d+) keys and a key threshold of (?P<threshold>\d+)')  # noqa

Response = namedtuple('Response', 'cmd stdout stderr code')


class CLIError(Exception):
    pass


class VaultCLI:
    def __init__(self, config):
        self.config = config

    def initialize(self, shares=None, threshold=None):
        cmd = ['vault', 'init']
        if shares:
            cmd.extend(['-key-shares', str(shares)])
        if threshold:
            cmd.extend(['-key-threshold', str(threshold)])
        response = self(cmd)

        contents = response.stdout.decode('utf-8')
        keys = PATTERN_KEYS.findall(contents)
        root_token = PATTERN_ROOT.search(contents).groups('token')[0]
        shares, threshold = PATTERN_CRITERIAS.search(contents).groups()
        self.config.update({
            'keys': set(keys),
            'shares': int(shares),
            'threshold': int(threshold),
            'root_token': root_token,
        })
        return True

    def unseal(self):
        for key in self.config.keys:
            cmd = ['vault', 'unseal', key]
            response = self(cmd)
        return response

    def audit_syslog(self):
        cmd = ['vault', 'audit-enable', 'syslog']
        response = self(cmd)
        if response.code:
            raise Exception(response.stderr.decode('utf-8'))

    def audit_file(self, path):
        cmd = ['vault', 'audit-enable', 'file', 'path=%s' % path]
        response = self(cmd)
        if response.code:
            raise Exception(response.stderr.decode('utf-8'))

    def __call__(self, cmd):
        env = os.environ.copy()
        env.setdefault('GOMAXPROCS', '2')
        if hasattr(self.config, 'csr'):
            env.setdefault('VAULT_CAPATH', self.config.csr)
        if hasattr(self.config, 'root_token'):
            env.setdefault('VAULT_TOKEN', self.config.root_token)
        shell = not isinstance(cmd, (list, tuple))
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, env=env, shell=shell)
        stdout, stderr = proc.communicate()
        if not proc.returncode:
            return Response(cmd, stdout, stderr, proc.returncode)
        raise CLIError(stderr.decode('utf-8'), proc.returncode)
