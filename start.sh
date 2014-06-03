#!/bin/bash
cd ~/Projects/blox
source venv/bin/activate
gunicorn -b 0.0.0.0:5000 blox:app -w 4 &
