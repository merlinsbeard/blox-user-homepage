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

def ip_addresses():
    f = open('config', 'r')
    ALL_IP = eval(f.read())
    f.close()
    IP = False
    if ALL_IP['wlan'] != '0.0.0.0':
        IP = ALL_IP['wlan']
    else:
        IP = ALL_IP['eth']
    ALL_IP['IP'] = IP
    return ALL_IP

@app.route('/')
def index():
    ALL_IP = ip_addresses()
    dicts = {
        'ALL_IP': ALL_IP,
        'IP': ALL_IP['IP'],
        }
    return render_template('index.html', dicts=dicts)

@app.route('/contactus')
def contactus():
    ALL_IP = ip_addresses()
    return render_template('contactus.html',dicts=ALL_IP)

@app.route('/howto')
def howto():
    ALL_IP = ip_addresses()
    dicts = {
        'All_IP': ALL_IP,
        'IP': ALL_IP['IP'] ,
        }
    return render_template('howto.html', dicts=dicts)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
