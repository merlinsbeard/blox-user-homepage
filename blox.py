import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template

# configuration

DATABASE = False

# create our little application
app = Flask(__name__)
# pulls in app configuration by looking for UPPERCASE variables
app.config.from_object(__name__)


@app.route('/')
def index():
	f = open('config', 'r')
	ALL_IP = eval(f.read())
	f.close()
	IP = False
	if ALL_IP['wlan'] != '0.0.0.0':
	    IP = ALL_IP['wlan']
	else:
	    IP = ALL_IP['eth']
	dicts = {
	    'ALL_IP': ALL_IP,
	    'IP': IP,
	    'db': DATABASE,
	    }
	return render_template('index.html', dicts=dicts)

@app.route('/contactus')
def contactus():
	return render_template('contactus.html')

if __name__ == '__main__':
	app.run(debug=False)
