#!/bin/sh
cd py_APIs/news_API
export FLASK_APP=news_API.py
python -m pipenv run flask --debug run -h 0.0.0.0 -p 5000 &


cd ..; cd ..;
cd py_APIs/original_API
export FLASK_APP=original_API.py
python -m pipenv run flask --debug run -h 0.0.0.0 -p 8080 &

