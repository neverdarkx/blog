from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, InputRequired, \
    EqualTo
from wtforms import ValidationError
from ..models import  User


class LoginForm(FlaskForm):
    email  = StringField('Email',[InputRequired(),Email()])
    password = PasswordField('Password', [InputRequired()])
    remember = BooleanField('remember me', )
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField('Email', [InputRequired(), Email()])
    username = StringField('Username',[InputRequired(),Length(1,64)])
    password = PasswordField('Password',[InputRequired(),
                            EqualTo('confirm',message='Password must match')])
    confirm = PasswordField('Repeat Password')
    agree = BooleanField('agree with our ***')
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('The Email has been used')

    def validate_agree(self,field):
        if not field.data:
            raise ValidationError('u must agree with ***')
    #此处显示错误有问题，需要看看form的文档

class ChangePwForm(FlaskForm):
    old_pw = PasswordField('Old Password', [InputRequired()])
    new_pw = PasswordField('New_password', [InputRequired(),
                            EqualTo('confirm',message='Password must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('确认')
