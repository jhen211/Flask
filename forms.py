from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField,
    DecimalField, DateTimeField, SelectField
)
from wtforms.validators import DataRequired, Length, Email, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Register')

class RecordForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired()])
    subcategory = StringField('Subcategory', validators=[Optional()])
    amount = DecimalField('Amount', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    recorded_at = DateTimeField(
        'Recorded At',
        format='%Y-%m-%d %H:%M:%S',
        validators=[DataRequired()]
    )
    submit = SubmitField('Save')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Save')
