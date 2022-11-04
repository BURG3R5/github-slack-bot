#!/bin/bash

#create virtual environment
python3 -m venv venv

#activate the vitual env
source venv/bin/activate

#install the required dependencies for env
pip install -r requirements.txt

#install the hooks
if ! hash pre-commit &> /dev/null ; then
    pip install pre-commit
    pre-commit install
fi
