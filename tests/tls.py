#!/usr/bin/env python3

import configparser
import json
import os
import os.path
import subprocess
from collections import OrderedDict

here = os.path.dirname(os.path.abspath(__file__))


def generate_keys(directory, crt, csr, key):
    # 1. generate configuration file
    env = os.environ.copy()

    config = configparser.ConfigParser()
    config.optionxform = str

    config['req'] = {
        'default_bits': '1024',
        'distinguished_name': 'req_distinguished_name',
        'req_extensions': 'v3_req',
        'prompt': 'no',
    }

    config['req_distinguished_name'] = {
        'C': 'GB',
        'ST': 'Test State or Province',
        'L': 'Test Locality',
        'O': 'AIOVault Name',
        'OU': 'AIOVault Testing',
        'CN': 'AIOVault',
        'emailAddress': 'test@email.address',
    }

    config['v3_req'] = OrderedDict([
        ('basicConstraints', 'CA:TRUE'),
        ('keyUsage', 'nonRepudiation,digitalSignature,keyEncipherment'),
        ('subjectAltName', '@alt_names'),
    ])

    config['alt_names'] = OrderedDict([
        ('DNS.1', 'kb.example.com'),
        ('DNS.2', 'helpdesk.example.org'),
        ('DNS.3', 'systems.example.net'),
        ('IP.1', '192.168.1.1'),
        ('IP.2', '192.168.69.14'),
        ('IP.3', '127.0.0.1'),
    ])

    config_filename = os.path.join(directory, 'openssl.ini')
    with open(config_filename, 'w') as file:
        config.write(file)
        env['OPENSSL_CONF'] = config_filename

    # 2. generate keys
    key_filename = os.path.join(directory, key)
    csr_filename = os.path.join(directory, csr)
    crt_filename = os.path.join(directory, crt)

    args = [
        'openssl', 'req',
        '-x509',
        '-nodes',
        '-days', '365',
        '-newkey', 'rsa:2048',
        '-keyout', key_filename,
        '-out', csr_filename,
        '-config', config_filename
    ]
    proc = subprocess.Popen(args,
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            cwd=directory)
    stdout, stderr = proc.communicate()
    if not proc.returncode:
        print('created:', key_filename)
        print('created:', csr_filename)
    else:
        raise Exception(stderr)

    args = [
        'openssl', 'x509',
        '-in', csr_filename,
        '-extfile', config_filename,
        '-extensions', 'v3_req',
        '-signkey', key_filename,
        '-out', crt_filename
    ]
    proc = subprocess.Popen(args,
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            cwd=directory)
    stdout, stderr = proc.communicate()

    if not proc.returncode:
        print('created:', crt_filename)
    else:
        raise Exception(stderr.decode('utf-8'))


def generate_config(directory, config, crt, key):
    data = {
        'backend': {
            'inmem': {}
        },
        'listener': {
            'tcp': {
                'address': '127.0.0.1:8200',
                'tls_cert_file': crt,
                'tls_key_file': key
            }
        }
    }
    filename = os.path.join(directory, config)
    with open(filename, 'w') as file:
        file.write(json.dumps(data, indent=2))


def run_server(directory, config):
    args = ['vault', 'server', '-config', config]
    proc = subprocess.Popen(args, cwd=directory)
    print(proc)


def handle_keys(args, parser):
    crt = 'server.crt'
    csr = 'server.csr'
    key = 'server.key'
    generate_keys(args.directory, crt, csr, key)


def handle_config(args, parser):
    config = 'server.json'
    crt = 'server.crt'
    key = 'server.key'
    generate_config(args.directory, config, crt, key)


def handle_server(args, parser):
    config = 'server.json'
    run_server(args.directory, config)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('generate tls and server config')
    parser.add_argument('--directory', default=os.path.join(here, 'certs'))
    subparsers = parser.add_subparsers(title='commands')

    parser_a = subparsers.add_parser('tls', help='generate keys')
    parser_a.set_defaults(handle=handle_keys)

    parser_b = subparsers.add_parser('configuration', help='generate config')
    parser_b.set_defaults(handle=handle_config)

    parser_c = subparsers.add_parser('run', help='run server')
    parser_c.set_defaults(handle=handle_server)

    try:
        args = parser.parse_args()
        os.makedirs(args.directory, exist_ok=True)
        args.handle(args, parser)
    except AttributeError:
        parser.print_help()
