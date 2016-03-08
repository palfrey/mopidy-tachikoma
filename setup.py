from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    with open(filename) as fh:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fh.read()))
        return metadata['version']

setup(
    name='Mopidy-Tachikoma',
    version=get_version('mopidy_tachikoma/__init__.py'),
    url='https://github.com/palfrey/mopidy-tachikoma',
    license='GNU Affero General Public License, Version 3',
    author='Tom Parker',
    author_email='palfrey@tevp.net',
    description='Mopidy extension for talking to Slack',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'slackclient',
        'Mopidy >= 1.0',
        'Pykka >= 1.1',
    ],
    entry_points={
        'mopidy.ext': [
            'tachikoma = mopidy_tachikoma:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
