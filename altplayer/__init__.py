from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)

mongoclient = MongoClient()
db = mongoclient['altplayer']
db.programmes.create_index([('pid', 'text')], unique=True)

import altplayer.views
