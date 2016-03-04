#!/bin/bash
virtualenv --system-site-packages ENV
source ENV/bin/activate
pip install --upgrade pip pip-tools
