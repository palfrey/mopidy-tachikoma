#!/bin/bash
virtualenv ENV --system-site-packages
source ENV/bin/activate
pip install --upgrade pip pip-tools
