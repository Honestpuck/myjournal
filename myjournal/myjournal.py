# all the imports
import os
import sqlite3
import time
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField, TextAreaField 
from wtforms.validators import Required

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

bootstrap = Bootstrap(app)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'myjournal.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('MYJ_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

## views

class PostForm(FlaskForm):
	title = StringField('Title')
	text = TextAreaField('Body', validators=[Required()])
	submit = SubmitField('Post')

@app.route('/', methods=['GET', 'POST'])
def show_entries():
    db = get_db()
    cur = db.execute('select title, text, createtime from entries order by id desc')
    entries = cur.fetchall()
    title = None
    text = None
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        text = form.text.data
    	db = get_db()
    	db.execute('insert into entries (title, text, createtime) values (?, ?, ?)', \
    		[title, text, time.time()])
    	db.commit()
    	flash('New entry was successfully posted')
    	return redirect(url_for('show_entries'))
    return render_template('show_entries.html', \
    	entries=entries, form=form, title=title, text=text)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.template_filter('fmttime')
def fmttime(value, format="%a, %b %d %Y, %H:%M"):
	tm = time.localtime(value)
	return time.strftime(format, tm)

import markdown2

mdExt = [
	"code-friendly",
	"fenced-code-blocks",
	"smarty-pants",
	"tables"
	]

@app.template_filter('mdown')
def mdown(value):
	md = markdown2.Markdown(extras=mdExt)
	return md.convert(value)




