from .config import init_db, db
from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    mongo.init_app(app)
    return mongo
