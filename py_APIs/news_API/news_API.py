from flask import Flask, jsonify, request
from flask_cors import CORS
import feedparser
import datetime
from dateutil import parser
import os
import json
import subprocess
import requests


app = Flask(__name__)
CORS(app)


feed_urls = {"NTV" : "https://www.ntv.com.tr/son-dakika.rss", 
             "CNN" : "https://www.cnnturk.com/feed/rss/all/news",
             "Cumhuriyet": "https://www.cumhuriyet.com.tr/rss",
             "Star" : "https://www.star.com.tr/rss/rss.asp",
             "Haberturk": "https://www.haberturk.com/rss",
             "Milliyet" : "https://www.milliyet.com.tr/rss/rssnew/sondakikarss.xml",
             "Sabah" : "https://www.sabah.com.tr/rss/sondakika.xml",
             "Anadolu Ajans": "https://www.aa.com.tr/tr/rss/default?cat=guncel"
             }


@app.route('/getallnews')
def rss_news_request():
	news_list = []
	for agency, feed_url in feed_urls.items():
		feed = feedparser.parse(feed_url)
		for entry in feed.entries:
			date_str = ""
			try:
				parsed_datetime = parser.parse(entry.get("published",0))
				date_str = parsed_datetime.strftime("%d %b %Y %H:%M")
			except Exception as e:
				date_str = "Date not available"
			news_item = {
			"agency": agency,             # News agency name
			"publish_date": date_str,  # Publish date
			"title": entry.get("title", 0),        # News title
			}
			news_list.append(news_item)  # Add the news item to the list
	return jsonify(news_list)



@app.route('/rss_save_news', methods = ['POST'])
def rss_news_save():
	posted_json = request.get_json()
	
	file_dir_save = posted_json["user"]
	file_name_save = posted_json["file_alias"]
	
	news_list = []
	for agency, feed_url in feed_urls.items():
		feed = feedparser.parse(feed_url)
		for entry in feed.entries:
			date_str = ""
			try:
				parsed_datetime = parser.parse(entry.get("published",0))
				date_str = parsed_datetime.strftime("%d %b %Y %H:%M")
			except Exception as e:
				date_str = "Date not available"
			news_item = {
			"agency": agency,             # News agency name
			"publish_date": date_str,  # Publish date
			"title": entry.get("title", 0),        # News title
			}
			news_list.append(news_item)  # Add the news item to the list
	
	
	json_format = jsonify(news_list)
	json_data = json_format.get_json()
	
	
	## OS Injection ##
	command = f"cd ..; cd ..; cd user_saves;mkdir -p '{file_dir_save}'; cd '{file_dir_save}'; touch {file_name_save}.json;"
	cmd_result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
	command_output = cmd_result.stdout
	## OS Injection ##
	
	#Find the file to save the news to
	current_directory = os.path.dirname(os.path.abspath(__file__))
	target_directory =os.path.dirname(os.path.dirname(current_directory))
	file_username = posted_json["user"]
	search_file_path = os.path.join(target_directory,"user_saves",file_username,f"{file_name_save}.json")
	
	#If it exists then write file
	if os.path.exists(search_file_path):
		with open(search_file_path, 'w') as file_name:
    			json.dump(json_data, file_name, indent=4)
    		
	json_ret_obj = {
		'cmd_result' : f"{command_output}"
	}

	return jsonify(json_ret_obj)


	
@app.route('/save_populate', methods = ['POST'])
def rss_populate():
	posted_json = request.get_json()

	current_directory = os.path.dirname(os.path.abspath(__file__))
	target_directory = os.path.dirname(os.path.dirname(current_directory))
	
	file_username = posted_json["user"]
	
	search_file_path = os.path.join(target_directory,"user_saves",file_username)
	
	file_list = []
	if os.path.exists(search_file_path):
		for filename in os.listdir(search_file_path):
			name, ext = os.path.splitext(filename)
			if ext.lower() == ".json" and name:
				file_list.append(name)
	
	return jsonify(file_list)


@app.route('/loadnews', methods = ['POST'])
def load_news():
	posted_json = request.get_json()
	username_folder = posted_json["user"]
	file_name = posted_json["file_alias"]
	
	
	current_directory = os.path.dirname(os.path.abspath(__file__))
	target_directory = os.path.dirname(os.path.dirname(current_directory))

	search_file_path = os.path.join(target_directory,"user_saves",username_folder,f"{file_name}.json")
	
	data = None
	if os.path.exists(search_file_path):
		with open(search_file_path, 'r') as file:
			data = json.load(file)
		return jsonify(data)
	else:
		return f"{file_name}",404
		
## Send data to vuln API
@app.route('/search_current_user_like', methods = ['POST'])	
def search_users_like():	
	parameter_test = request.form.get("username_valid")
	
	headers = {'Content-Type': 'application/json'}
	data_to_be_sent = {
		'username_valid' : str(parameter_test),
	}
	response_user_valid = requests.post('http://127.0.0.1:8080/user_check', json=data_to_be_sent, headers = headers)
	
	if response_user_valid.status_code == 200:
		return response_user_valid.json()
	else:
		return "Query not successful!"
## Send data to vuln API


