import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, request, flash, send_from_directory
from werkzeug.utils import secure_filename
from mpd import MPDClient
import subprocess
from slugify import slugify
import glob
from PIL import Image, ImageOps


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
    desktop = ['bsd','linux','macos','solaris','windows'],
    smartphones = ['android','iphone','ipad'],
    SECRET_KEY='development key',
))

ALLOWED_EXTENSIONS_PICTURE = set(['jpg','jpeg','png','gif']),

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
        Connects to MPD Server
    '''
    client = MPDClient()
    IP = ip_addresses()
    IP = IP['IP']
    client.connect(IP, 6600)
    client.password('blox')
    return client

def get_root_dirs_files():
    '''
        Returns a dict containing the paths of pictures and Pictures Folder,
        Inside the static/uploads/pictures folder.
    '''
    main_path = os.path.dirname(os.path.abspath('__file__'))
    new_path = main_path + '/static/uploads/Pictures'
    path_subtract = main_path + '/static/'
    dirs_files = {}

    for root, dirs, files in os.walk(new_path):
        relative_path = root.replace(path_subtract,"")
        new_key = slugify(relative_path)
        folder_name = relative_path.replace("uploads/Pictures/","")
        if files:
            tm = files[0]
        else:
            #tm = url_for("static",filename="images/tm.jpg")
            tm = False
        dirs_files[new_key] = {
                'relative_path': relative_path,
                'dirs': dirs,
                'files': files,
                'folder_name': folder_name,
                'thumb': tm,
                }
    return dirs_files

def create_thumbs(directory):
    '''
        Creates thumbs for the specified directory.
        Saves the thumbs in folder static/thumbs/
    '''
    size = 180,180
    thumb_directory = 'static/thumbs/'
    image_extensions = ('jpg','jpeg',
                        'png','gif',
                        'tiff')

    # Gets all files in directory
    for infile in glob.glob(directory + "/*.*"):
        f, ext = os.path.splitext(infile)

        # Checks if a file is image
        if ext[1:].lower() in image_extensions:

            # Gets the path of image
            # Creates a path for the thumbnail image
            path = os.path.dirname(infile)
            path = path.replace("static/", "", 1)
            path = thumb_directory + path

            # If path of thumbnail is not existing
            # Create the directory and its sub-directories
            if not os.path.exists(path):
                os.makedirs(path)

            # get the bare filename of image without extensions
            filename = os.path.basename(f)

            # Pillow does not like jpg so convert it to jpeg
            if ext.lower() == ".jpg":
                ext = ".jpeg"

            # Open the image if it does not yet have a thumbnail
            if not glob.glob(path + "/" + filename + ext):
                im = Image.open(infile)

                # Creates a new thumbnail for none GIF
                # Gif images are not converted just
                # resave
                #if ext.lower() not in ('gif'):
                #    im.thumbnail(size, Image.ANTIALIAS)
                im = ImageOps.fit(im, size, method=Image.ANTIALIAS)

                # Save the image with its appropriate
                # name and extension
                im.save(path + "/" + filename + ext, ext[1:])

#@app.route('/hi')
def hi():
    # Used for checking if thumbs are working
    directory = "static/uploads/Pictures"
    create_thumbs(directory)
    return "success"


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
    # Index webpage
    ALL_IP = ip_addresses()
    dicts = {
        'ALL_IP': ALL_IP,
        'IP': ALL_IP['IP'],
        'using_desktop': using_desktop(),
        }
    return render_template('index.html', dicts=dicts)

@app.route('/powercontrol', methods=['GET', 'POST'])
def powercontrol():
    # Has Power button for shutdown and
    # Reboot button for reboot

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


def allowed_file_music(filename):
    # Checks if a file uploaded is an mp3 ,flac, or wav

    filename = filename.lower()
    allowed_extensions = ['mp3', 'wav','flac']
    return '.' in filename and \
            filename.rsplit('.',1)[1] in allowed_extensions
            #filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS_MUSIC

def allowed_file_picture(filename):
    # Checks if a file uploaded is an image

    filename = filename.lower()

    allowed_extensions = ['jpg','jpeg','png','gif','raw',]
    return '.' in filename and \
            filename.rsplit('.',1)[1] in allowed_extensions

#@app.route('/uploadsample', methods=['GET','POST'])
def upload_sample():
    # Upload page for sample
    # Used for testing purposes
    ALL_IP = ip_addresses()
    dicts = {
            'ALL_IP': ALL_IP,
            'IP': ALL_IP['IP'],
            'using_desktop': using_desktop(),
            }
    if request.method == 'POST':
            files = request.files.getlist('file[]')
            for file in files:
                    if file and allowed_file_music(file.filename):
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
    # Upload page for Music

    ALL_IP = ip_addresses()
    dicts = {
            'ALL_IP': ALL_IP,
            'IP': ALL_IP['IP'],
            'using_desktop': using_desktop(),
            }
    if request.method == 'POST':
            files = request.files.getlist('file[]')
            for file in files:
                    if file and allowed_file_music(file.filename):
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


@app.route('/pictures', methods=['GET', 'POST'])
def pictures():
    dir_and_files = get_root_dirs_files()
    pictures = dir_and_files
    ALL_IP = ip_addresses()
    dicts = {
        'ALL_IP': ALL_IP,
        'IP': ALL_IP['IP'],
        'using_desktop': using_desktop(),
        }

    if request.method == 'POST':
        directory = request.form['directory']
        main_path = os.path.dirname(os.path.abspath('__file__')) \
            + '/static/uploads/Pictures/' + directory

        if not os.path.exists(main_path):
            os.makedirs(main_path)
            os.chown(main_path, 1000, 1000)
            return redirect(url_for('albums', slug=slugify('uploads/Pictures'+'-'+ directory)))

    return render_template('pictures.html', dicts=dicts, pictures=pictures)

@app.route('/pictures/<slug>',methods=['GET','POST'])
def albums(slug):
    dir_and_files = get_root_dirs_files()
    ALL_IP = ip_addresses()
    dicts = {
        'ALL_IP': ALL_IP,
        'IP': ALL_IP['IP'],
        'using_desktop': using_desktop(),
        }
    try:
        dir_and_files = dir_and_files[slug]
    except:
        return 'Album / folder not existing'

    # Put Pictures in thumbnails
    directory_path = 'static/' + dir_and_files['relative_path']
    create_thumbs(directory_path)

    if request.method == 'POST':
        #if request.form['upload']:
        if 'upload' in request.form.values():
            files = request.files.getlist('file[]')
            for file in files:
                if file and allowed_file_picture(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER_MUSIC'], filename)
                    main_path = os.path.dirname(os.path.abspath('__file__'))
                    file_path = main_path + '/static/' + dir_and_files['relative_path'] + '/' + filename
                    file.save(file_path)
                    #return redirect(url_for('uploaded_file',filename=filename))
                    os.chmod(file_path, 0755)
                    os.chown(file_path, 1000, 1000)
                else:
                    return '<h1>Failed to Upload files. Make sure the files are jpg,png,or gif.</h1>'
            #return '<h1>Succesfully uploaded Music</h1>'
            return redirect(url_for('albums',slug=slug))
        elif 'rename' in request.form.values():
            return 'rename'
        else:
            if not session.get('logged_in'):
                return redirect(url_for('login'))
            else:
                a = request.form.values()
                a = a[0]
                relative_filename =  str(a)
                main_path = os.path.dirname(os.path.abspath('__file__'))
                full_path = main_path+ '/' + 'static' + '/' + relative_filename
                thumb_image_path = main_path + '/' + 'static/thumbs/' + relative_filename
                thumb_image_path= thumb_image_path.replace('jpg','jpeg')
                os.remove(thumb_image_path)
                os.remove(full_path)
                return '<h1>Successfully deleted image</h1>'+ full_path + "</br> <a href=>back</a>"

    return render_template('albums.html', dicts=dicts, pictures=dir_and_files)

#@app.route('/multiple', methods=['GET','POST'])
def multiple():
    # sample multiple button
    # testing purposes

    if request.method == 'POST':
        if 'Delete' in request.form.values():
            a = request.form['delete']
            return a
        elif 'Upload' in request.form.values():
            return 'Upload'

    return render_template('multiple.html')

_file_directory = '/home/blox/Public/'
@app.route('/public')
def public_directory():
    """
        Shows files in the Download directory of blox
    """
    output_html = '<html><ul>{0}<ul></html>'
    href_tag = '<li><a href="/public/{0}">{0}</a></li>'
    file_links = ''
    for filename in os.listdir(_file_directory):
        if os.path.isfile(_file_directory + filename):
            file_links += href_tag.format(filename)
    #return output_html.format(file_links)
    ALL_IP = ip_addresses()
    dicts = {
        'ALL_IP': ALL_IP,
        'IP': ALL_IP['IP'],
        'using_desktop': using_desktop(),
        }
    return render_template('public_files.html', file_links=file_links, dicts=dicts)

@app.route('/public/<path:filename>')
def send_file(filename):
    # Makes the files downloadable directyle
    return send_from_directory(_file_directory, filename)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
