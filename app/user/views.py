# -*- coding: utf-8 -*-
from flask import flash, render_template, redirect, url_for, g
from flask_login import login_required, current_user
from app import app, db
from .models import User
from .forms import UserForm
from app.post.models import Post
from config import POSTS_PER_PAGE
from flask_babel import gettext

@app.before_request
def before_request():
    g.user = current_user

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if not user:
        flash(gettext('User %(name)s not found', name=nickname))
        return redirect(url_for('index'))
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html', user=user, posts=posts)



@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = UserForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.email = form.email.data
        g.user.about_me = form.about_me.data

        db.session.add(g.user)
        db.session.commit()
        flash(gettext('Your changes have been saved.'))
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.email.data = g.user.email
        form.about_me.data = g.user.about_me
        return render_template('edit.html', form=form)


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash(gettext('User %(name)s not found.', name=nickname))
        return redirect(url_for('index'))
    if user == g.user:
        flash(gettext('You can\'t follow yourself!'))
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash(gettext('Cannot follow %(name)s.', name=nickname))
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash(gettext('You are now following %(name)s!', name=nickname))
    return redirect(url_for('user', nickname=nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash(gettext('You can\'t unfollow yourself!'))
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash(gettext('Cannot unfollow %(name)s.', name=nickname))
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash(gettext('You have stopped following %(name)s', name=nickname))
    return redirect(url_for('user', nickname=nickname))