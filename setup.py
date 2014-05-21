# -*- coding: utf8 -*-

from setuptools import setup

setup(
    name='hookit',
    version='0.8.2',
    packages=['hookit'],
    license='MIT License',
    keywords='git github webhook webhooks',
    description='Bind GitHub WebHooks to actions',
    install_requires=['docopt >= 0.6.0', 'github3.py >= 0.9.0', 'netaddr >= 0.7.11'],
    author='Samuel Bishop',
    author_email='sam@psyx.co',
    url='https://github.com/techdragon/hookit',
    entry_points={
        'console_scripts': ['hookit = hookit:run'],
    }
)
