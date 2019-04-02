""" Main catalog application.
 """
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db',connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def homePage():
    return 'Home Page'




if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)