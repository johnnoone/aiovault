#!/usr/bin/env python

from setuptools import setup

with open('README.rst') as file:
    content = file.read()

setup(
    name='aiovault',
    version='0.1',
    description='Vault wrapper for asyncio',
    long_description=content,
    author='Xavier Barbosa',
    author_email='clint.northwood@gmail.com',
    url='https://github.com/johnnoone/aiovault',
    packages=[
        'aiovault'
    ],
    keywords=[
        'infrastructure',
        'asyncio',
        'key/value store'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: System :: Clustering',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking :: Monitoring',
    ],
    install_requires=[
        'aiohttp>=0.15.2',
        'stevedore>=0.9'
    ],
    extras_require={
        ':python_version=="3.3"': ['asyncio'],
    },
    entry_points={
        'aiovault.audit.backend': [
            'file = aiovault.v1.audit.backends:FileBackend',
            'syslog = aiovault.v1.audit.backends:SyslogBackend'
        ],
        'aiovault.auth.backend': [
            'app-id = aiovault.v1.auth.backends:AppIDBackend',
            'cert = aiovault.v1.auth.backends:CertBackend',
            'github = aiovault.v1.auth.backends:GitHubBackend',
            'token = aiovault.v1.auth.backends:TokenBackend',
            'userpass = aiovault.v1.auth.backends:UserPassBackend'
        ],
        'aiovault.secret.backend': [
            'aws = aiovault.v1.secret.backends:AWSBackend',
            'consul = aiovault.v1.secret.backends:ConsulBackend',
            'generic = aiovault.v1.secret.backends:GenericBackend',
            'mysql = aiovault.v1.secret.backends:MySQLBackend',
            'postgresql = aiovault.v1.secret.backends:PostgreSQLBackend',
            'transit = aiovault.v1.secret.backends:TransitBackend'
        ]
    }
)
