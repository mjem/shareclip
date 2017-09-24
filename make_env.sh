#!/bin/bash
virtualenv --python=python3 env
. env/bin/activate
pip install -f requirements.txt
pip install -f requirements-dev.txt
