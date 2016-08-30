# -*- coding: utf-8 -*-
from flask import render_template, g, flash, redirect, url_for, request
from flask_login import login_required
from datetime import datetime
from app import app, db
from app.post.forms import PostForm
from app.post.models import Post
from config import POSTS_PER_PAGE
from app import babel
from config import LANGUAGES
from flask_babel import gettext

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())

@app.before_request
def before_request():
    g.locale = get_locale()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    user = g.user
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=user)
        db.session.add(post)
        db.session.commit()
        flash(gettext('Your post is now live!'))
        return redirect(url_for('index'))
    posts = user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html', title='Home', user=user,  posts=posts, form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
