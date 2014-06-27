import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, request
from werkzeug.utils import secure_filename
from mpd import MPDClient


f = open('config', 'r')
music_folder = eval(f.read())
f.close()
UPLOAD_FOLDER = music_folder['music_upload_folder']


ALLOWED_EXTENSIONS = set(['mp3'])

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

def using_desktop():
    desktop_os = ['bsd','linux','macos','solaris','windows']
    smartphones = ['android','iphone','ipad']
    userAgentString = request.headers.get('User-Agent')
    user_agent = request.user_agent
    platform = user_agent.platform
    desktop = False
    if platform in desktop_os:
        desktop = True
    return desktop

def connect_mpd():
    client = MPDClient()
    IP = ip_addresses()
    IP = IP['IP']
    client.connect(IP, 6600)
    client.password('blox')
    return client


@app.route('/')
def index():
    ALL_IP = ip_addresses()
    dicts = {
        'ALL_IP': ALL_IP,
        'IP': ALL_IP['IP'],
        'using_desktop': using_desktop(),
        }
    return render_template('index.html', dicts=dicts)
#
desktop = ['bsd','linux','macos','solaris','windows']
smartphones = ['android','iphone','ipad']

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload_music', methods=['GET','POST'])
def upload_file():
	ALL_IP = ip_addresses()
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		}
	if request.method == 'POST':
		files = request.files.getlist('file')
		for file in files:
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				#return redirect(url_for('uploaded_file',filename=filename))
			else:
				return '<h1>Failed to Upload files. Make sure the files are mp3.</h1>'
		return '<h1>Succesfully uploaded Music</h1>'

	return render_template('upload_music.html', dicts=dicts)




@app.route('/user-agent')
def getUserAgent():
    userAgentString = request.headers.get('User-Agent')
    user_agent = request.user_agent
    platform = user_agent.platform
    linux = False
    windows = False
    android = False
    desktop_or_laptop = False
    smartphone_or_others = False
    ua = dir(user_agent)

    desktops = False

    if platform in desktop:
        desktop_or_laptop = True
        desktops = True

    if platform in smartphones:
        smartphone_or_others = True

    return render_template('user-agent.html', userAgentString=userAgentString,
        user_agent=user_agent, platform=platform, linux=linux, ua=ua, desktops=desktops)

@app.route('/music')
def music():
    ALL_IP = ip_addresses()
    dicts = {
        'ALL_IP': ALL_IP,
        'IP': ALL_IP['IP'],
        }

    return render_template('music.html', dicts=dicts)

@app.route('/controlmusic',methods=['GET','POST'])
def control_music():
    ALL_IP = ip_addresses()
    dicts = {
        'ALL_IP': ALL_IP,
        'IP': ALL_IP['IP'],
        }

    client = connect_mpd()
    if request.method == 'POST':
        if 'Play' in request.form.values():
            client.play()
        elif 'Pause' in request.form.values():
            client.pause()
        if 'Next' in request.form.values():
            client.next()
        elif 'Previous' in request.form.values():
            client.previous()
        elif '+' in request.form.values():
            original_volume = client.status()['volume']
            original_volume = int(original_volume)
            client.setvol(original_volume+2)
        elif '-' in request.form.values():
            original_volume = client.status()['volume']
            original_volume = int(original_volume)
            client.setvol(original_volume-2)

    STATUS = client.status()
    CURRENT_SONG = client.currentsong()

    return render_template('control_music.html', dicts=dicts,  STATUS=STATUS, CURRENT_SONG=CURRENT_SONG)

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
