from flask_wtf import Form
from wtforms import StringField, PasswordField, RadioField
from wtforms.validators import DataRequired, EqualTo

from wifi import Cell

cell = Cell.all('wlan0')
ssid=[]
CHOICES=[]
for c in cell:
	ssid.append(c.ssid)

for i in ssid:
	CHOICES.append((i,i))

class AddUser(Form):
	username = StringField('Username', 
		validators=[DataRequired()])
	password = PasswordField('Password', 
		validators=[DataRequired()])

class ChangePass(Form):
	password = PasswordField('Password', 
		validators=[DataRequired(), EqualTo('password1', message="Passwords must match")])
	password1 = PasswordField('Confirm Password', 
		validators=[DataRequired()])

class ConnectWifi(Form):
	ssid = RadioField('ssid', choices=CHOICES)
	password = PasswordField('Password')
