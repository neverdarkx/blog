from flask import render_template, redirect, url_for, abort, flash, request, current_app
from flask_login import login_required, current_user
from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms.fields import SubmitField
from . import main
from .forms import TodoForm, EditForm, CommentForm, PostForm, EditArtForm
from .. import db
from ..models import User, List, Comment, Label, History

#主页所有人都能访问，所以不能写成login_required
@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = List.query.order_by(List.timestamp.desc()).paginate(
        page, per_page=current_app.config['MAPLEZ_LISTS_PER_PAGE'],
        error_out=False)
    # if current_user.is_authenticated:
    lists = pagination.items
    labels = Label.query.order_by(Label.body).all()
    return render_template('Index.html',
                           lists=lists, labels=labels,
                           Comment=Comment, pagination=pagination)
    # return render_template('Index.html')

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    comments = Comment.query.filter_by(author_id=user.id).limit(5)
    labels = Label.query.order_by(Label.body).all()
    histories = History.query.all()
    return render_template('user.html', user=user,
                           labels=labels, histories=histories)

@main.route('/user/edit')
@login_required
def edit():
    form = EditForm()
    user = current_user
    form.email.data = '178278676@qq.pom'
    #貌似没必要调用这个，除非参数就是原对象._get_current_object()
    if form.validate_on_submit():
        user.username = form.username.data
        user.about_me = form.about_me.data
        db.session.add(user)
        #不清楚到底要不要，等下再看看狗书
        #db.session.commit()
        return redirect(url_for('main.user', username=user.username))
    return render_template('edit.html', form=form, user=user)

@main.route('/article/<id>', methods=['GET', 'POST'])
def article(id):
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            comment = Comment(body=form.body.data,
                              author_id=current_user.id,
                              list_id=int(id),
                              username=current_user.username)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('main.article', id=int(id)))
    list = List.query.filter_by(id=int(id)).first()
    comments = Comment.query.filter_by(list_id=int(id)).order_by(db.desc(Comment.timestamp)).all()
    labels = Label.query.order_by(Label.body).all()
    return render_template('article.html',
                           form=form, comments=comments, list=list, labels=labels)


#感觉编辑功能和长传功能是有重复的地方的，以后再想想咋回事

@main.route('/post', methods=['GET','POST'])
@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        list = List(title=form.title.data,
                    subtitle=form.subtitle.data,
                    summary=form.summary.data,
                    body=form.body.data,
                    image = form.image.data,
                    author_id=current_user.id,
                    username=current_user.username)
        # db.session.add(list)
        # db.session.commit()
        for label in form.label.data.split(','):
            label = label.strip()
            label = label.upper()
            lab = Label.query.filter_by(body=label).first()
            if lab is None and label:
                lab = Label(body=label)
                db.session.add(lab)
                db.session.commit()
            list.labels.append(lab)
            db.session.add(list)
        flash('You post an article')
        return redirect(url_for('main.index'))
    return render_template('post.html', form=form)

#需要验证当前用户,以后再加
@main.route('/edit_art/<id>', methods=['GET','POST'])
@login_required
def edit_art(id):
    form = PostForm()
    list = List.query.filter_by(id=int(id)).first()
    labels = list.labels.all()
    str = ''
    for label in labels:
        str = str + label.body + ','
    if form.validate_on_submit():
        list.title = form.title.data
        list.subtitle = form.subtitle.data
        list.image = form.image.data
        list.summary = form.summary.data
        list.body = form.body.data
        db.session.add(list)
        for label in list.labels.all():
            print(label)
            list.labels.remove(label)
            db.session.add(list)
            if list.labels == 0:
                db.session.delete(list)
        db.session.commit()
        for label in form.label.data.split(','):
            #绝了，这个token空间真的是垃圾，各种bug，狗屎
            if label:
                label = label.strip()
                label = label.upper()
                lab = Label.query.filter_by(body=label).first()
                if lab is None and label:
                    lab = Label(body=label)
                    db.session.add(lab)
                list.labels.append(lab)
        db.session.commit()
        flash('You post an article')
        return redirect(url_for('main.article', id=list.id))
    form.label.data = str
    print(str)
    return render_template('edit_art.html', form=form,
                           list=list, str=str)

@main.route('/list/<classify>')
def list_class(classify):
    pass

@main.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    list = List.query.filter_by(id=id).first()
    db.session.delete(list)
    db.session.commit()
    return redirect(url_for('.index'))

@main.route('/complete/<id>', methods=['GET', 'POST'])
def complete(id):
    list = List.query.filter_by(id=id).first()
    #暂定为删除操作
    db.session.delete(list)
    db.session.commit()
    return redirect(url_for('.index'))