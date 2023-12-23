from flask import Flask, jsonify, request
from flask_cors import CORS
import feedparser

app = Flask(__name__)
CORS(app)


feed_urls = {"NTV" : "https://www.ntv.com.tr/son-dakika.rss", 
             "CNN" : "https://www.cnnturk.com/feed/rss/all/news",
             "Cumhuriyet": "https://www.cumhuriyet.com.tr/rss",
             "Star" : "https://www.star.com.tr/rss/rss.asp",
             "BBC" : "https://feeds.bbci.co.uk/turkce/rss.xml",
             "Haberturk": "https://www.haberturk.com/rss",
             "Milliyet" : "https://www.milliyet.com.tr/rss/rssnew/sondakikarss.xml",
             "Sabah" : "https://www.sabah.com.tr/rss/sondakika.xml",
             "Sozcu" : "https://www.sozcu.com.tr/feeds-son-dakika",
             "Anadolu Ajans": "https://www.aa.com.tr/tr/rss/default?cat=guncel"
             }


@app.route('/getallnews')
def rss_news_request():
    
    feed_all_parsed = dict({})
    for key in feed_urls.keys():
        feed_all_parsed[key] = feedparser.parse(feed_urls[key])

    title_ret = dict({})
    for key in feed_all_parsed.keys():
        list_news_call = list(feed_all_parsed[key].entries)
        title_list = [str(item.title) for item in list_news_call]
        title_ret[key] = title_list


    return jsonify(title_ret)


