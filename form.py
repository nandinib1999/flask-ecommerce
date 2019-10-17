from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField, PasswordField, BooleanField

from wtforms import validators, ValidationError

class CustomerForm(FlaskForm):
   Name = TextField("Name",[validators.Required("Please enter your name.")])
   Gender = SelectField('Gender', choices = [('F', 'Female'), 
      ('M', 'Male')])
   Address = TextAreaField("Address")
   City = TextField("City")
   State = TextField("State")
   Pin = TextField("Pin")
   Country = TextField("Country")
   Email = TextField("Email",[validators.Required("Please enter your email address."),
      validators.Email("Please enter your email address.")])
   Code = SelectField('code', choices = [('+91', '+91'), ('+1', '+1')])
   Mobile = TextField("Mobile", [validators.Length(min=10, max=10)])
   Password = PasswordField('Password', [validators.Required('Please Enter Password')])
   accept_rules = BooleanField('I accept the site rules', [validators.InputRequired()])
   submit = SubmitField("Submit")