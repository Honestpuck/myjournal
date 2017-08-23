# all the imports
import os
import sqlite3 # deprecated
import time
from flask import Flask, request, session, g, redirect, url_for, abort, \
	 render_template, flash, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField, TextAreaField 
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_script import Manager

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , myjournal.py

bootstrap = Bootstrap(app)
manager = Manager(app)

# Load default config and override config from an environment variable
app.config.update(dict(
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default',
	SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.root_path, 'myjournal.db'),
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True,
	SQLALCHEMY_TRACK_MODIFICATIONS = False,
))
app.config.from_envvar('MYJ_SETTINGS', silent=True)

# Database stuff
db = SQLAlchemy(app)

class Entry( db.Model):
	 __tablename__ = 'entries' 
	 id = db.Column( db.Integer, primary_key = True) 
	 title = db.Column(db.Text, nullable=True) 
	 text = db.Column(db.Text)
	 createtime = db.Column(db.Integer, index=True)
	 
	 def __repr__( self): 
		return '< Entry %r >' % self.title

## views

class PostForm(FlaskForm):
	title = StringField('Title')
	text = TextAreaField('Body', validators=[Required()])
	submit = SubmitField('Post')

@app.route('/', methods=['GET', 'POST'])
def show_entries():
	Entry.query.order_by('id desc')
	entries = Entry.query.all()
	title = None
	text = None
	form = PostForm()
	if form.validate_on_submit():
		title = form.title.data
		text = form.text.data
		post = Entry(title=title, text=text, createtime=time.time())
		db.session.add(post)
		db.session.commit()
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

if __name__ == '__main__':
	manager.run()


