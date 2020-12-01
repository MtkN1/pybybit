# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='pybybit',
    packages=['pybybit', 'pybybit.util'],
    version='2.0.1',
    description='Bybit API client library for Python',
    author='ueebee',
    url='https://github.com/ueebee/pybybit',
    install_requires=['requests', 'websocket_client']
)
