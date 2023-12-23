#!/bin/sh
cd /home/depletedsandwich/Desktop/turkish_news_API/py_APIs/news_API
export FLASK_APP=news_API.py
python -m pipenv run flask --debug run -h 0.0.0.0 -p 5000 &

cd /home/depletedsandwich/Desktop/turkish_news_API/py_APIs/original_API
export FLASK_APP=original_API.py
python -m pipenv run flask --debug run -h 0.0.0.0 -p 8080 &

