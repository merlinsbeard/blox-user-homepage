#!/bin/bash
# This is a sample start.sh 
# configure this to be used on your system

cd /var/www/html/blox/blox-user-homepage
source ../venv/bin/activate
#python thumbs.py True
#source venv/bin/activate
gunicorn -b 0.0.0.0:5000 blox:app -w 4 --error-logfile error.log --log-file log.log &
