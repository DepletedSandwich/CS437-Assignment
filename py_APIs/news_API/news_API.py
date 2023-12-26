from flask import Flask, jsonify, request
from flask_cors import CORS
import feedparser
import datetime
from dateutil import parser

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


