from flask import Flask, jsonify, request, redirect, url_for, session, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import requests
import json
import subprocess
import re
from sqlalchemy.sql import text

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_info.db'
CORS(app, supports_credentials=True)
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
	
	reg_success_msg = session.get('registration_success') #Session Variable holding register success
	session.pop('registration_success', None)
	
	out_success_msg = session.get('logout_success') #Session Variable holding logout success
	session.pop('logout_success', None)
	
	return render_template('welcome.html', reg_scc_msg=reg_success_msg, out_scc_msg=out_success_msg)
	
@app.route('/admin_login', methods = ['GET']) #Admin login page template
def login_admin():
	return render_template('news_admin_index_login.html', warning_message = None)

@app.route('/member_login', methods = ['GET']) #Member login page template
def login_member():
	return render_template('news_index_login.html', warning_message = None)
    
@app.route('/member_register', methods = ['GET']) #Member register page template
def register_member():
	return render_template('news_index_register.html')
    
@app.route('/news_feed', methods = ['GET']) #News Feed Render to user
@login_required
def feed_load():
	feed_response = requests.get('http://127.0.0.1:5000/getallnews')
	return render_template('prod_table.html',table_fill = feed_response.json())
#### Static html pages hosted ####
#### Render Redirect ####
@app.route('/redirect_feed', methods = ['GET'])
@login_required
def redirect_feed():
	return redirect("/news_feed")
	
@app.route('/redirect_save_news', methods = ['GET'])
@login_required
def redirect_save():
	return redirect("/save_news")
#### Render Redirect ####

#### Saving News ####

@app.route('/save_news', methods = ['GET']) #Render saving page for user
@login_required
def load_save_news_GET():
	server_response_fault = session.get('server_fault')
	session.pop('server_fault', None)

	server_response_success= session.get('server_success')
	session.pop('server_success', None)
	
	options = []
	username = ""
	
	if current_user.is_authenticated:
		username = str(current_user.username)
		headers = {'Content-Type': 'application/json'}
		data_to_be_sent = {
			'user' : username
		}
		response_populate = requests.post('http://127.0.0.1:5000/save_populate', json=data_to_be_sent, headers = headers)
		if response_populate.status_code in [200,302]:
			options = response_populate.json()
		else:
			session['server_fault'] = 'Request not successful!'
	else:
		logout_user()
		session['logout_success'] = 'You are logged out!'
		return redirect('/welcome')
	
	return render_template('save_news_OS.html', fault_response = server_response_fault, success_response = server_response_success, population_list = options, user = username)

@app.route('/send_save_auth', methods = ['POST']) 
@login_required
def save_news_auth():
	if current_user.is_authenticated:
		auth_user = current_user.username
		file_name_save = request.form['file_name']
		headers = {'Content-Type': 'application/json'}
		data_to_be_sent = {
			'user' : str(auth_user),
			'file_alias' : str(file_name_save)
		}
		response_save = requests.post('http://127.0.0.1:5000/rss_save_news', json=data_to_be_sent, headers = headers)
		
		#Handle Response
		if response_save.status_code in [200,302]:
			session['server_success'] = response_save.json()
		else:
			session['server_fault'] = 'Request not successful!'
			
		return redirect('/save_news') 
		
	else:
		logout_user()
		session['logout_success'] = 'You are logged out!'
		return redirect('/welcome')
#### Saving News ####

#### Loading News ####
@app.route('/load_news', methods = ['POST']) 
@login_required
def load_user_news():
	if current_user.is_authenticated:
		posted_json = request.get_json()
		file_alias = posted_json["select_option"]
		auth_user = current_user.username
		
		
		headers = {'Content-Type': 'application/json'}
		data_to_be_sent = {
			'user' : str(auth_user),
			'file_alias' : str(file_alias)
		}
		
		response_load = requests.post(f'http://127.0.0.1:5000/loadnews', json=data_to_be_sent, headers = headers)
		#Handle Response
		if response_load.status_code in [200,302]:
			return response_load.json()
		else:
			return jsonify({"error": f"Cannot find {response_load.text}"}), 404
			
	else:
		logout_user()
		session['logout_success'] = 'You are logged out!'
		return redirect('/welcome')

#### Loading News ####

#### Login and Session Management APIs ####
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/member_login', methods = ['POST']) #Logic of member login
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

@app.route('/member_register', methods = ['POST']) #Logic of member register
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
		warning_message = 'Username not valid!'
		return render_template('news_index_register.html', warning_message=warning_message)

	if existing_email:
		warning_message = 'Email not valid!'
		return render_template('news_index_register.html', warning_message=warning_message)
	
	#Check Username validity
	if not re.match(r'^[a-zA-Z0-9_-]+$', username):
		warning_message = 'Username contains invalid characters!'
		return render_template('news_index_register.html', warning_message=warning_message)
	
	
	# Create a new User instance and add it to the database
	new_user = User(username=username, password=password, email=email)
	db.session.add(new_user)
	db.session.commit()
	
	session['registration_success'] = 'Registration Successful'
	
	return redirect('/welcome')
	

@app.route('/admin_login', methods = ['POST']) # Admin Login Logic
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

@app.route('/logout', methods = ['GET']) #User logout logic
@login_required
def logout():
    logout_user()
    session['logout_success'] = 'You are logged out' 
    return redirect('/welcome')
#### Login and Session Management APIs ####

#### Check whether user exists #### This endpoint is vulnerable to sql injection demonstrating API vuln
@app.route('/user_check', methods = ['POST'])
def check_user_validity():
	posted_json = request.get_json()
	username_valid = posted_json["username_valid"]
	
	query_string = f"SELECT * FROM user WHERE username='{username_valid}'"
	query = text(query_string)
	with db.engine.connect() as con:
		rs = con.execute(query)
		result = rs.fetchall()
	final_result = [{"user_exists": row[1]} for row in result]

	return jsonify(final_result)
#### Check whether user exists ####
