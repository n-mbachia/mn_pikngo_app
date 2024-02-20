# forms.py

from flask_wtf import FlaskForm
from wtforms import FileField, StringField, PasswordField, SubmitField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
import uuid

class AdminSignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    verification_code = StringField('Verification Code', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_verification_code(self, field):
        if field.data != '123456':  # Replace '123456' with your actual verification code
            raise ValidationError('Invalid verification code')

class ContentForm(FlaskForm):
    id = uuid.uuid4()
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif']), FileSize(max_size=2 * 1024 * 1024)])  # 2 MB limit
    submit = SubmitField('Submit')
    author = StringField('Author')
