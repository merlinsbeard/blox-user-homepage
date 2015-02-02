import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, request, flash, send_from_directory
from werkzeug.utils import secure_filename
from mpd import MPDClient
import subprocess
from slugify import slugify
import glob
from PIL import Image, ImageOps, ImageFile
from flask import request
import thumbs
from math import ceil
from markdown import markdown
import json
from os import system
from forms import AddUser, ChangePass


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
import time
def sort_files_by_mdate(list_files, relative_path):
	main_path = os.path.abspath('static/'+relative_path)
	date_file_list = []
	new_list = []
	for f in list_files:
		stats = os.stat(main_path+'/'+f)
		lastmod_date = time.localtime(stats[8])
		date_file_tuple = lastmod_date, f
		date_file_list.append(date_file_tuple)
	date_file_list.reverse()
	for new_f in date_file_list:
		new_list.append(new_f[1])
	return new_list

def get_root_dirs_files():
	'''
			Returns a dict containing the paths of pictures and Pictures Folder,
			Inside the static/uploads/pictures folder.
	'''
	main_path = os.path.dirname(os.path.abspath('__file__'))
	new_path = main_path + '/static/uploads/Pictures'
	path_subtract = main_path + '/static/'
	dirs_files = {}

	items_per_page = 10
	pages = 0

	for root, dirs, files in os.walk(new_path):
		relative_path = root.replace(path_subtract,"")
		new_key = slugify(relative_path)
		folder_name = relative_path.replace("uploads/Pictures/","")
		if files:
			files = sort_files_by_mdate(files, relative_path)
			tm = files[0]
			pages = ceil(float(len(files))/items_per_page)
			pages_dict = {}
			if len(files) < items_per_page:
				pages_dict[0] = []
				for item in files:
					pages_dict[0].append(item)
			else:
				for n in range(int(pages)):
					pages_dict[n]=[]

				initial_page = 0
				for item in sorted(files):
					pages_dict[initial_page].append(item)
					if len(pages_dict[initial_page]) == items_per_page:
						initial_page += 1

		else:
			pages_dict=False
			#tm = url_for("static",filename="images/tm.jpg")
			tm = False

		dirs_files[new_key] = {
					'relative_path': relative_path,
					'dirs': sorted(dirs),
					'files': files,
					'folder_name': folder_name,
					'thumb': tm,
					'files_2': pages_dict,
					}
	return dirs_files

ImageFile.LOAD_TRUNCATED_IMAGES = True
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
				#		 im.thumbnail(size, Image.ANTIALIAS)
				im = ImageOps.fit(im, size, method=Image.ANTIALIAS)

				# Save the image with its appropriate
				# name and extension
				im.save(path + "/" + filename + ext, ext[1:])

def create_thumbs2(directory, image_name):
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
	for infile in glob.glob(directory + image_name):
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
				#		 im.thumbnail(size, Image.ANTIALIAS)
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




@app.route('/')
def index():
	# Index webpage
	url = request.url_root
	url = url[7:-1]
	ALL_IP = ip_addresses()
	f = open('markdown.txt','r')
	filestring = f.read()
	filestring = markdown(filestring)
	#with open('config.txt','r') as f:
	#	json_data = json.load(f)
	#	banner = json_data['home_banner']
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
		'message': filestring,
		#'banner' : banner
		}

	return render_template('index.html', dicts=dicts,url=url)




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
	url = request.url_root
	url = url[7:-1]
	dicts = {
			'ALL_IP': ALL_IP,
			'IP': ALL_IP['IP'],
			'using_desktop': using_desktop(),
			'url': url,
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
	url = request.url_root
	url = url[7:-1]
	dicts = {
			'ALL_IP': ALL_IP,
			'IP': ALL_IP['IP'],
			'using_desktop': using_desktop(),
			'url': url,
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
	url = request.url_root
	url = url[7:-1]
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
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
	url = request.url_root
	url = url[7:-1]
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
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
	url = request.url_root
	url = url[7:-1]
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
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

@app.route('/pictures/<slug>/', defaults={'page':0},methods=['GET','POST'])
@app.route('/pictures/<slug>/<int:page>',methods=['GET','POST'])
def pages(slug, page):
	ALL_IP = ip_addresses()
	url = request.url_root
        url = url[7:-1]
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
		}
	try:
		dir_and_files = get_root_dirs_files()
		dir_and_files2 = dir_and_files[slug]['files_2'][page]
		dicts['pictures'] = dir_and_files2
		dicts['num_of_page'] = dir_and_files[slug]['files_2']
		dicts['image_url'] = dir_and_files[slug]['relative_path']
		dicts['slug'] = slug
		dicts['page'] = page
		if page != len(dir_and_files[slug]['files_2']):
			dicts['next'] = page + 1
		if page > 0:
			dicts['previous'] = page - 1
		for image in dicts['pictures']:
			create_thumbs2(dicts['image_url'], image)
			print 'create_thumbs'

	except TypeError:
		dicts['error_message'] = 'No images yet upload images'
	except KeyError:
		dicts['error_message'] = "Page not available"


	if request.method == 'POST':
		#if request.form['upload']:
		if 'upload' in request.form.values():
			files = request.files.getlist('file[]')
			for file in files:
				if file and allowed_file_picture(file.filename):
					filename = secure_filename(file.filename)
					file_path = os.path.join(app.config['UPLOAD_FOLDER_MUSIC'], filename)
					main_path = os.path.dirname(os.path.abspath('__file__'))
					file_path = main_path + '/static/' + dir_and_files[slug]['relative_path'] + '/' + filename
					file.save(file_path)
					os.chmod(file_path, 0755)
					os.chown(file_path, 1000, 1000)
				else:
					return '<h1>Failed to Upload files. Make sure the files are jpg,png,or gif.</h1>'

			return redirect(url_for('albums',slug=slug))
		elif 'rename' in request.form.values():
			return 'rename'
		elif 'front' in request.form.values():
			a = request.form.values()
			a = a[0]

			return '<h1>%s</h1>' % a
		else:
			return 'none'
			#if not session.get('logged_in'):
			#	return redirect(url_for('login'))
			#else:
			#	a = request.form.values()
			#	a = a[0]
			#	relative_filename =  str(a)
			#	main_path = os.path.dirname(os.path.abspath('__file__'))
			#	full_path = main_path+ '/' + 'static' + '/' + relative_filename
			#	os.remove(full_path)
			#	return '<h1>Successfully deleted image</h1>'+ full_path + "</br> <a href=>back</a>"


	return render_template('pages.html', dicts=dicts,)

@app.route('/pictures/<slug>/<name>/front', methods=['GET','POST'])
def frontimage(slug, name):
	if request.method == 'POST':
		dir_and_files = get_root_dirs_files()
		slug = slug
		name = name
		name = name.replace('%',' ')
		a = dir_and_files[slug]
		image = url_for('static', filename=a['relative_path'] +'/'+name)

		with open('config.json', 'r+') as f:
			json_data = json.load(f)
			json_data['home_banner'] = image
			f.seek(0)
			f.write(json.dumps(json_data))
			f.truncate()
		return "successfully updated front image <a href='/'>Back</a>"
	else:
		return redirect('/')

@app.route('/pictures/<slug>',methods=['GET','POST'])
def albums(slug):
	dir_and_files = get_root_dirs_files()
	ALL_IP = ip_addresses()
	url = request.url_root
	url = url[7:-1]
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
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
	url = request.url_root
	url = url[7:-1]
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
		}
	return render_template('public_files.html', file_links=file_links, dicts=dicts)

@app.route('/public/<path:filename>')
def send_file(filename):
	# Makes the files downloadable directyle
	return send_from_directory(_file_directory, filename)


@app.route('/message')
def message():
	ALL_IP = ip_addresses()
	url = request.url_root
	url = url[7:-1]
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
		}
	f = open('markdown.txt','r')
	filestring = f.read()
	filestring = markdown(filestring)
	return render_template('message.html', dicts=dicts, filestring=filestring)


############## SETTINGS #################


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
			return redirect(url_for('settings'))
	return render_template('login.html', error=error,dicts=dicts)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('index'))

@app.route('/settings/powercontrol', methods=['GET', 'POST'])
def powercontrol():
	# Has Power button for shutdown and
	# Reboot button for reboot

	if not session.get('logged_in'):
		return redirect(url_for('login'))
		
	ALL_IP = ip_addresses()
	url = request.url_root
	url = url[7:-1]
	dicts = {
			'ALL_IP': ALL_IP,
			'IP': ALL_IP['IP'],
			'using_desktop': using_desktop(),
			'url': url,
			}
	if request.method == 'POST':
		if 'Power' in request.form.values():
			subprocess.call('poweroff')
		elif 'Reboot' in request.form.values():
			subprocess.call('reboot')
		elif 'Thumbnails' in request.form.values():
			thumbs.opt(True)
	return render_template('power.html',dicts=dicts)


def list_of_users():
	# Returns Lists of home users with uid between 1000 and 2000
	infile = '/etc/passwd'
	
	with open(infile) as f:
		f = f.readlines()

	users = []
	for user in f:
		user = user.split(':')

		if int(user[2]) >= 1000 and int(user[2]) < 2000:
			users.append(user)

	return users


@app.route('/settings')
def settings():
	ALL_IP = ip_addresses()
	url = request.url_root
	url = url[7:-1]
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
		}
	return render_template('settings.html', dicts=dicts)

@app.route("/settings/usermanage")
def all_users():
	ALL_IP = ip_addresses()
	url = request.url_root
	url = url[7:-1]
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
		}
	# Shows all users
	users = list_of_users()
	return render_template('all_users.html', users=users, dicts=dicts)

@app.route("/settings/adduser" ,methods=['GET','POST'])
def add_user():
	# Adds user directly to the system, including samba
	ALL_IP = ip_addresses()
	url = request.url_root
	url = url[7:-1]
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
		}

	if not session.get('logged_in'):
		return redirect(url_for('login'))

	form = AddUser(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			username = form.username.data
			password = form.password.data

			users = list_of_users()
			for u in users:
				if username == u[0]:
					return 'Username already existing'

			cmd_useradd = "useradd -G blox " + username + " -s /bin/bash -m"
			cmd_password = "./password.sh " + username + ' ' + password
			system(cmd_useradd)
			system(cmd_password)
			return "<h2>Successfully Added Acount " + username + '. ' + '<a href="' + url_for('all_users') + '"> Go Back </a>'
		else:
			return 'fails'

	else:
		return render_template('add_user.html', form=form, dicts=dicts)


@app.route("/settings/usermanage/<int:uid>", methods=['GET','POST'])
def solo_user(uid):
	# returns indiidual user depending on UID
	ALL_IP = ip_addresses()
	url = request.url_root
	url = url[7:-1]
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
		}
	users = list_of_users()
	solo_user = 'User not existing'

	for u in users:
		if int(u[3]) == uid: 
			solo_user = u

	return render_template('solo_user.html', solo_user=solo_user, dicts=dicts)
    #return render_template('user.html')

@app.route("/settings/usermanage/<int:uid>/changepass", methods=['GET','POST'])
def changepass_user(uid):
	# CHanges password of user

	if not session.get('logged_in'):
		return redirect(url_for('login'))

	ALL_IP = ip_addresses()
	url = request.url_root
	url = url[7:-1]
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
		}
	form = ChangePass(request.form)
	users = list_of_users()
	solo_user = 'User not existing'



	for u in users:
		if int(u[3]) == uid: 
			solo_user = u

	if request.method == 'POST':
		if form.validate_on_submit():
			password = form.password.data
			cmd_password = "./password.sh " + solo_user[0] + ' ' + password
			system(cmd_password)
			return '<h2>Successfully Changed Password. ' + '<a href="' + url_for('all_users') + '"> Go Back </a></h2>'

	return render_template('change_pass.html', form=form, solo_user=solo_user, dicts=dicts)

@app.route("/settings/usermanage/<int:uid>/remove", methods=['GET','POST'])
def remove_user(uid):
	# Removes user

	if not session.get('logged_in'):
		return redirect(url_for('login'))

	ALL_IP = ip_addresses()
	url = request.url_root
	url = url[7:-1]
	dicts = {
		'ALL_IP': ALL_IP,
		'IP': ALL_IP['IP'],
		'using_desktop': using_desktop(),
		'url': url,
		}
	users = list_of_users()

	for u in users:
		if int(u[3]) == uid: 
			solo_user = u

			if solo_user[0] == 'blox':
				return 'Cannot Remove Blox' + '<a href="' + url_for('all_users') + '"> Go Back </a>'
			else:
				if request.method == 'POST':
					cmd = 'deluser --remove-home ' + solo_user[0]
					system(cmd)
					return 'Removed ' + solo_user[0] + '<a href="' + url_for('all_users') + '"> Go Back </a>'
		
	return render_template('remove_user.html', solo_user=solo_user, dicts=dicts)




if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
