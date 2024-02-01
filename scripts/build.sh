#!/bin/bash
python3.11 -m pip install --upgrade pip
python3.11 -m pip install pipenv
python3.11 -m pipenv requirements > requirements.txt
python3.11 -m pip install -r requirements.txt

