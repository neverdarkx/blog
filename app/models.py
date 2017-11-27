from datetime import datetime
import hashlib
import bleach
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager


class Permission:
    ADMINISTER = 1
    NORMALUSER = 0


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    about_me = db.Column(db.Text)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    #头像等下研究
    #photo = db.
    lists = db.relationship('List', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('**********')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def passwordverify(self,password):
        return check_password_hash(self.password_hash,password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

#感觉就是一个VIEW，把两个表的ID拿出来了，便于检索，不知道对不对
#也不对这个应该就是一个真的表__tables__这个，多对多相关的数据应该是就存在这里面？？？
#注意外键是用表名而不是类名访问的！！
classTags = db.Table('classTags',
    db.Column('list_id', db.Integer, db.ForeignKey('lists.id')),
    db.Column('label_id', db.Integer, db.ForeignKey('labels.id'))
)


class List(db.Model):
    __tablename__ = 'lists'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True)
    subtitle = db.Column(db.String(20))
    summary = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String(64))
    #多对多关系模型，云笔记有详细内容
    #服气了这里这个LabeList
    labels = db.relationship('Label',
                            secondary=classTags,
                            backref=db.backref('lists', lazy='dynamic'),
                            lazy='dynamic')
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        # 需要转换的标签
        allowed_tags = [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
            'h1', 'h2', 'h3', 'p', 'img'
        ]
        # 需要提取的标签属性，否则会被忽略掉
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt']
        }
        target.body_html = bleach.linkify(
            bleach.clean(
                markdown(value, output_format='html'),
                tags=allowed_tags,
                attributes=attrs,
                strip=True
            )
        )


db.event.listen(List.body, 'set', List.on_changed_body)


class Label(db.Model):
    __tablename__ = 'labels'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(10), index=True)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), index=True)
    username = db.Column(db.String(64))


class History(db.Model):
    __tablename__ = 'histories'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    # 这里关于类的实例有些疑问
    # 静态方法应该没错，如果每一行都是一个类的实例的话？？？
    # 有道理啊，没想过数据库记录究竟是什么存在方式...等下看看相关的代码
    @staticmethod
    def auto_ten(user):
        if History.query.filter_by(author_id=user.id).count() > 10:
            h = History.query.filter_by(author_id=user.id).order_by(History.timestamp).first()
            db.session.delete(h)
            db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def can(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
