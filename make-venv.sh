#!/bin/bash
set -e
virtualenv ENV --system-site-packages -p python2.7
source ENV/bin/activate
pip install --upgrade pip pip-tools