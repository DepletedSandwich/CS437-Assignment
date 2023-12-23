from flask import Flask, jsonify, request, redirect, url_for, session, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_info.db'
CORS(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

#### User Table Template ####
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(70), nullable=False)

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(70), nullable=False)

#### User Table Template ####

#### Static html pages hosted ####
@app.route('/welcome', methods = ['GET'])
def welcome():
	db.create_all()
	success_message = session.get('registration_success')
	session.pop('registration_success', None)
	
	return render_template('welcome.html', confirmation_message=success_message)
	
@app.route('/admin_login', methods = ['GET'])
def login_admin():
	return render_template('news_admin_index_login.html', warning_message = None)

@app.route('/member_login', methods = ['GET'])
def login_member():
	return render_template('news_index_login.html', warning_message = None)
    
@app.route('/member_register', methods = ['GET'])
def register_member():
	return render_template('news_index_register.html')
    
@app.route('/news_feed', methods = ['GET'])
@login_required
def feed_load():
	return render_template('prod_table.html')
#### Static html pages hosted ####

#### Login and Session Management APIs ####
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/member_login', methods = ['POST'])
def login_member_post():
	username = request.form['username']
	password = request.form['password']

	if not username or not password:
		warning_message = 'Empty Fields!'
		return render_template('news_index_login.html',warning_message = warning_message)

	user = User.query.filter_by(username=username).first()
	
	if not user:
		warning_message = 'Incorrect Credentials!'
		return render_template('news_index_login.html',warning_message = warning_message)

	if user.password == password:
		login_user(user)
		return redirect(url_for('feed_load'))
	else:
		warning_message = 'Incorrect Credentials!'
		return render_template('news_index_login.html',warning_message = warning_message)

@app.route('/member_register', methods = ['POST'])
def register_member_post():
	username = request.form['username']
	password = request.form['password']
	email = request.form['email']

	if not username or not password or not email:
		warning_message = 'Empty Fields!'
		return render_template('news_index_register.html',warning_message = warning_message)

	# Check if the username or email already exists in the database
	existing_user = User.query.filter_by(username=username).first()
	existing_email = User.query.filter_by(email=email).first()

	if existing_user:
		warning_message = 'Username already exists.'
		return render_template('news_index_register.html', warning_message=warning_message)

	if existing_email:
		warning_message = 'Email address already in use.'
		return render_template('news_index_register.html', warning_message=warning_message)

	# Create a new User instance and add it to the database
	new_user = User(username=username, password=password, email=email)
	db.session.add(new_user)
	db.session.commit()
	
	session['registration_success'] = 'Registration Successful'
	
	return redirect('/welcome')
	

@app.route('/admin_login', methods = ['POST'])
def login_admin_post():
	username = request.form['username']
	password = request.form['password']

	if not username or not password:
		warning_message = 'Empty Fields!'
		return render_template('news_admin_index_login.html',warning_message = warning_message)

	admin = Admin.query.filter_by(username=username).first()
	
	if not admin:
		warning_message = 'Incorrect Credentials!'
		return render_template('news_admin_index_login.html',warning_message = warning_message)

	if admin.password == password:
		login_user(admin)
		return "<h1>You are logged in as admin!</h1>"
	else:
		warning_message = 'Incorrect Credentials!'
		return render_template('news_admin_index_login.html',warning_message = warning_message)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'You are logged out.'
#### Login and Session Management APIs ####

