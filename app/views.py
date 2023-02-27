import functools
import re
from datetime import datetime

from flask import (Flask, escape, flash, g, redirect, render_template, request,
                   session, url_for)
from sqlalchemy import null
from werkzeug.security import check_password_hash, generate_password_hash

from . import anime_recommender, app
from .db import get_db


@app.route("/", methods=['GET', 'POST'])
def home():
    results = anime_recommender.get_random_animes()

    return render_template("home.html", results=zip(results['name'], results['image_url'])) #Implement age verification - DoB with sign-up, and/or +18 consent


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/contact/")
def contact():
    return render_template("contact.html")


@app.route("/search/", methods=['GET', 'POST'])
@app.route("/search/<name>", methods=['GET', 'POST'])
def search(name=None):
    if request.method == 'POST':
        anime = request.form['anime']

        if anime:
            results = anime_recommender.get_similar_names(partial=anime)

            if results.empty:
                return render_template("not_found.html")
            else:                
                return render_template("search.html", results=zip(results['name'], results['image_url'])) #Implement age verification - DoB with sign-up, and +18 consent

    return render_template("search.html")


@app.route("/details/")
@app.route("/details/<name>")
def details(name=None):
    if name is None:
        return render_template("not_found.html")

    result = anime_recommender.get_anime_details(name=name)

    image_url = result['image_url'].values[0]
    anime_genre = result['anime_genre'].values[0]
    anime_type = result['anime_type'].values[0]
    anime_episodes = result['anime_episodes'].values[0]
    anime_rating = result['anime_rating'].values[0]

    results = anime_recommender.get_similar_animes(query=name)

    return render_template("details.html", name=name, image_url=image_url, anime_genre=anime_genre, anime_type=anime_type, anime_episodes=anime_episodes, anime_rating=anime_rating, results=zip(results['name'], results['image_url']))


@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('login'))

        flash(error)

    return render_template('register.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home'))

        flash(error)

    return render_template('login.html')


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))

        return view(**kwargs)

    return wrapped_view
