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
    categories = session.query(Category).all()
    return render_template('index.html', categories = categories)

@app.route('/login', methods = ['GET','POST'])
def login():
    return 'Login Page'

@app.route('/logout', methods = ['POST'])
def logout():
    return 'Logout'

@app.route('/<category>/items')
def categoryItems(category):
    return 'List of items for category'

@app.route('/<category>/<item>')
def itemDetail(category, item):
    return 'Item Details Page'

@app.route('/<category>/items/new', methods = ['GET','POST'])
def newItem(category):
    return 'New Item Page'

@app.route('/<category>/<item>/edit', methods = ['GET','POST'])
def editItem(category, item):
    return 'Edit Item Page'

@app.route('/<category>/<item>/delete', methods = ['GET','POST'])
def deleteItem(category, item):
    return 'Delete Item Page'

@app.route('/api/categories')
def apiCategories():
    return 'Return all categories'

@app.route('/api/items')
def apiItems():
    return 'Return all items'

@app.route('/api/categories/<int:category_id>')
def apiCategory(category_id):
    return 'Return single category info.'


@app.route('/api/categories/<int:category_id>/items')
def apiCategoryItems(category_id):
    return 'Return all items for a category'

@app.route('/api/items/<int:item_id>')
def apiItem(item_id):
    return 'Return single item detail'


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)