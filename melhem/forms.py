from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from melhem.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Ulanyjy Ady',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Açar Sözi', validators=[DataRequired()])
    confirm_password = PasswordField('Açar Sözi Tassyklamak',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Ýazga Alyn')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu ulanyjy ady eýýäm alynan, başgasyny synanyşyň..')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu email adresi eýýäm ulgamda bar, başgasyny synanyşyň..')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Açar Sözi', validators=[DataRequired()])
    remember = BooleanField('Ýatda Sakla')
    submit = SubmitField('Ulgama Gir')
