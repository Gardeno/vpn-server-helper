#!/usr/bin/env bash

git pull
./venv/bin/pip install -r requirements.txt
touch reload
