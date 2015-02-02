from flask import Flask, render_template, request, url_for
from forms import AddUser, ChangePass
from os import system

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

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

@app.route("/settings")
def index():
	users = list_of_users()
	return render_template('all_users.html', users=users)

@app.route("/settings/adduser" ,methods=['GET','POST'])
def add_user():
	# Adds user directly to the system, including samba
	form = AddUser(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			username = form.username.data
			password = form.password.data

			users = list_of_users()
			for u in users:
				if username == u[0]:
					return 'Username already existing'

			cmd_useradd = "useradd " + username + " -s /bin/bash -m"
			cmd_password = "./password.sh " + username + ' ' + password
			system(cmd_useradd)
			system(cmd_password)
			return username + ' ' + password
		else:
			return 'fails'

	else:
		return render_template('add_user.html', form=form)

@app.route("/settings/usermanage")
def all_users():
	# Shows all users
	users = list_of_users()
	return render_template('all_users.html', users=users)

@app.route("/settings/usermanage/<int:uid>", methods=['GET','POST'])
def solo_user(uid):
	# returns indiidual user depending on UID
	users = list_of_users()
	solo_user = 'User not existing'

	for u in users:
		if int(u[3]) == uid: 
			solo_user = u

	return render_template('solo_user.html', solo_user=solo_user)
    #return render_template('user.html')

@app.route("/settings/usermanage/<int:uid>/changepass", methods=['GET','POST'])
def changepass_user(uid):
	# CHanges password of user
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
			return cmd_password

	return render_template('change_pass.html', form=form, solo_user=solo_user)

@app.route("/settings/usermanage/<int:uid>/remove", methods=['GET','POST'])
def remove_user(uid):
	# Removes user
	users = list_of_users()

	for u in users:
		if int(u[3]) == uid: 
			solo_user = u

			if solo_user[0] == 'blox':
				return 'Cannot Remove Blox'
			else:
				if request.method == 'POST':
					cmd = 'deluser --remove-home ' + solo_user[0]
					system(cmd)
					return 'Removed ' + solo_user[0]
		
	return render_template('remove_user.html', solo_user=solo_user)


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
