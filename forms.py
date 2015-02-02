from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo


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

