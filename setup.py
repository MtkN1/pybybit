# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='pybybit',
    packages=['pybybit', 'pybybit.util'],
    version='2.0.4',
    description='Bybit API client library for Python',
    author='MtkN1XBt',
    url='https://github.com/MtkN1/pybybit',
    install_requires=['requests', 'websocket_client']
)
