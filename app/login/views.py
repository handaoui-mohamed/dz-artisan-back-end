# -*- coding: utf-8 -*-
from flask import render_template, redirect, session, url_for, request, g, flash
from flask_login import login_user, logout_user, current_user
from datetime import datetime
from app import app, db, lm
import re
from .forms import LoginForm
from app.user.models import User
from flask_babel import gettext

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        user = User.query.filter_by(nickname=request.form['nickname']).first()
        if(not user):
            user = User(nickname=request.form['nickname'], email=request.form['email'], about_me='')
            user.nickname = re.sub('[^a-zA-Z0-9_\.]', '', user.nickname)
            db.session.add(user)
            db.session.commit()

            db.session.add(user.follow(user))
            db.session.commit()
        else:
            if(user.email != request.form['email']):
                flash(gettext('Wrong email or nickname'))
                return redirect(url_for('login'))

        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)
        login_user(user, remember=remember_me)
        return redirect(request.args.get('next') or url_for('index'))


    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))