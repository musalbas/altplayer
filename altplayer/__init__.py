from flask import Flask
from pymongo import MongoClient

from altplayer import iplayer

app = Flask(__name__)

mongoclient = MongoClient()
db = mongoclient['altplayer']

db.programmes.create_index([('pid', 'text')], unique=True)

programmes = iplayer.Programmes(db.programmes)

import altplayer.views
