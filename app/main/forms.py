from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from flask_pagedown.fields import PageDownField
from wtforms.validators import DataRequired, Length, Email, Regexp, InputRequired
from wtforms import ValidationError
from ..models import  User


class TodoForm(FlaskForm):
    text = TextAreaField('Add something')
    submit = SubmitField('Submit')


class EditForm(FlaskForm):
    email = StringField('Email')
    #需要显示一个已认证，以及修改email的按钮
    username = StringField('Username',[InputRequired(), Length(1,64)])
    about_me = TextAreaField('About Me', [Length(0,200)])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        pass

    #可以自动识别为对应的验证器，很神奇，有时间看看源码
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise 'The name has benn used!'


class PostForm(FlaskForm):
    title = StringField(u'主标题')
    subtitle = StringField(u'副标题')
    summary = TextAreaField(u'摘要')
    image = StringField(u'图片')
    label = StringField(u'标签')
    body = PageDownField(u'正文')
    submit = SubmitField(u'提交')


class EditArtForm(FlaskForm):
    title = StringField(u'主标题')
    subtitle = StringField(u'副标题')
    summary = TextAreaField(u'摘要')
    image = StringField(u'图片')
    label = StringField(u'标签')
    body = PageDownField(u'正文')
    submit = SubmitField(u'提交')

class CommentForm(FlaskForm):
    body = TextAreaField('Comment')
    submit = SubmitField('发表')