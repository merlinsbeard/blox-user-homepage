#!/bin/bash
# This is a sample start.sh 
# configure this to be used on your system

cd /home/blackbox/Projects/blox
source venv/bin/activate
gunicorn -b 0.0.0.0:5000 blox:app -w 4 &
