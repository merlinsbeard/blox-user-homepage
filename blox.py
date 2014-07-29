import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, request, flash
from werkzeug.utils import secure_filename
from mpd import MPDClient
import subprocess


f = open('config.txt', 'r')
folder = eval(f.read())
f.close()
# configuration
DATABASE = False

# create our little application
app = Flask(__name__)

# pulls in app configuration by looking for UPPERCASE variables
app.config.from_object(__name__)
app.config.update(dict(
    USERNAME='admin',
    PASSWORD='admin',
    UPLOAD_FOLDER_MUSIC = folder['music_upload_folder'],
    UPLOAD_FOLDER_PICTURE = folder['picture_upload_folder'],
    ALLOWED_EXTENSIONS = set(['mp3']),
    desktop = ['bsd','linux','macos','solaris','windows'],
    smartphones = ['android','iphone','ipad'],
    SECRET_KEY='development key',
))


def ip_addresses():
    '''
        Checks the config file for the IP address of BLOX
    '''
    f = open('config.txt', 'r')
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
    '''
        Checks if blox webpage is being browsed in desktops or
        in smartphones
    '''
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
    '''
        Connects to MPD client
    '''
    client = MPDClient()
    IP = ip_addresses()
    IP = IP['IP']
    client.connect(IP, 6600)
    client.password('blox')
    return client

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    ALL_IP = ip_addresses()
    dicts = {
        'ALL_IP': ALL_IP,
        'IP': ALL_IP['IP'],
        'using_desktop': using_desktop(),
        }
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
        #if request.form['username'] != "admin":
            error = 'Invalid Username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('powercontrol'))
    return render_template('login.html', error=error,dicts=dicts)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/')
def index():
    '''
        Index webpage
    '''
    ALL_IP = ip_addresses()
    dicts = {
        'ALL_IP': ALL_IP,
        'IP': ALL_IP['IP'],
        'using_desktop': using_desktop(),
        }
    return render_template('index.html', dicts=dicts)

@app.route('/powercontrol', methods=['GET', 'POST'])
def powercontrol():
    '''
        Has Power button for shutdown and
        Reboot button for reboot
    '''
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    ALL_IP = ip_addresses()
    dicts = {
            'ALL_IP': ALL_IP,
            'IP': ALL_IP['IP'],
            'using_desktop': using_desktop(),
            }
    if request.method == 'POST':
        if 'Power' in request.form.values():
            subprocess.call('poweroff')
        elif 'Reboot' in request.form.values():
            subprocess.call('reboot')
    return render_template('power.html',dicts=dicts)


def allowed_file(filename):
    '''
        Checks if a file uploaded is an mp3 or wav
    '''
    return '.' in filename and \
            filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploadsample', methods=['GET','POST'])
def upload_sample():
    '''
        Upload page for sample
    '''
    ALL_IP = ip_addresses()
    dicts = {
            'ALL_IP': ALL_IP,
            'IP': ALL_IP['IP'],
            'using_desktop': using_desktop(),
            }
    if request.method == 'POST':
            files = request.files.getlist('file[]')
            for file in files:
                    if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER_MUSIC'], filename)
                            file.save(file_path)
                            #return redirect(url_for('uploaded_file',filename=filename))
                            os.chmod(file_path, 0755)
                            os.chown(file_path, 1000, 1000)
                    else:
                            return '<h1>Failed to Upload files. Make sure the files are mp3.</h1>'
            return '<h1>Succesfully uploaded Music</h1>'

    return render_template('uploadsample.html', dicts=dicts)

@app.route('/uploadmusic', methods=['GET','POST'])
def upload_file():
    '''
        Upload page for Music
    '''
    ALL_IP = ip_addresses()
    dicts = {
            'ALL_IP': ALL_IP,
            'IP': ALL_IP['IP'],
            'using_desktop': using_desktop(),
            }
    if request.method == 'POST':
            files = request.files.getlist('file[]')
            for file in files:
                    if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER_MUSIC'], filename)
                            file.save(file_path)
                            #return redirect(url_for('uploaded_file',filename=filename))
                            os.chmod(file_path, 0755)
                            os.chown(file_path, 1000, 1000)
                    else:
                            return '<h1>Failed to Upload files. Make sure the files are mp3.</h1>'
            return '<h1>Succesfully uploaded Music</h1>'

    return render_template('upload_music.html', dicts=dicts)




@app.route('/user-agent')
def getUserAgent():
    '''
        Gets the useragent of the user
    '''
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

@app.route('/music', methods=['GET','POST'])
def music():
    '''
        contains info in connecting music
    '''
    ALL_IP = ip_addresses()
    dicts = {
        'ALL_IP': ALL_IP,
        'IP': ALL_IP['IP'],
        }

    client = connect_mpd()
    STATUS = client.status()
    CURRENT_SONG = client.currentsong()
    return render_template('music.html', dicts=dicts, STATUS=STATUS, CURRENT_SONG=CURRENT_SONG)

@app.route('/controlmusic',methods=['GET','POST'])
def control_music():
    '''
        Has basic controls in music
    '''
    ALL_IP = ip_addresses()
    dicts = {
        'ALL_IP': ALL_IP,
        'IP': ALL_IP['IP'],
        }

    client = connect_mpd()
    if request.method == 'POST':
        if 'Play' in request.form.values():
            if client.status()['state'] == 'pause':
                client.play()
            elif client.status()['state'] == 'play':
                client.pause()
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
    '''
        Info in contacts us
    '''
    ALL_IP = ip_addresses()
    return render_template('contactus.html',dicts=ALL_IP)

@app.route('/howto')
def howto():
    '''
        how to
    '''
    ALL_IP = ip_addresses()
    dicts = {
        'All_IP': ALL_IP,
        'IP': ALL_IP['IP'] ,
        }
    return render_template('howto.html', dicts=dicts)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
