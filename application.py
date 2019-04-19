""" Main catalog application.
 """
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask import session as login_session
import os
import httplib2
import json
import random, string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random, string
from models import Base, User, Category, Item

app = Flask(__name__)

app.secret_key = os.urandom(16)

STATE = ''


engine = create_engine('sqlite:///catalog.db',connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()



@app.route('/')
def homePage():
    categories = session.query(Category).all()
    return render_template('index.html', categories = categories, login_session=login_session)

@app.route('/login')
def login():
    STATE = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = STATE
    return render_template('login.html', STATE = STATE, login_session=login_session)


@app.route('/fbconnect', methods = ['POST'])
def fbConnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    token = access_token.decode('utf-8')
    """  app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    print('Token: {}\nID: {}\nSecret: {}\nToken Type: {}\n'.format(access_token, app_id, app_secret, type(access_token)))
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token.decode('utf-8'))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print(result)
    """

    # Use token to get user info from API
    """ userinfo_url = "https://graph.facebook.com/v3.2/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.decode('utf-8')['access_token'] #result.split(',')[0].split(':')[1].replace('"', '')
    #url = 'https://graph.facebook.com/v3.2/me?access_token=%s&fields=name,id,email' % access_token
    #h = httplib2.Http()
    #result = h.request(url, 'GET')[1]

    #userinfo_url = 'https://graph.facebook.com/v3.2/me'
    #token = result.split('&')[0] """

    url = 'https://graph.facebook.com/v3.2/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result.decode('utf-8'))
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    login_session['access_token'] = token

    url = 'https://graph.facebook.com/v3.2/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result.decode('utf-8'))

    login_session['picture'] = data['data']['url']
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    """ output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="' + login_session['picture']
    output += '" style="width: 300px; height: 300px; border-radius: 150px; '
    output += '-webkit-border-radius: 150px; -moz-border-radius: 150px">' """
    flash("You are now logged in as %s" %login_session['username'])
    return redirect(url_for('homePage'))


@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbDisconnect()
            del login_session['facebook_id']
        del login_session['user_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        flash('You have been successfully logged out.')
    else:
        flash('You were not logged in to begin with.')
    return redirect(url_for('homePage'))

@app.route('/<category>/items')
def categoryItems(category):
    return render_template('category.html', login_session=login_session)

@app.route('/<category>/<item>')
def itemDetail(category, item):
    return render_template('item.html', login_session=login_session)

@app.route('/items/new', methods = ['GET','POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    if request.method == 'POST':
        newItem = Item(name = request.form['name'],
            description = request.form['description'],
            user_id = login_session['user_id'],
            category_id = request.form['category'])
        session.add(newItem)
        session.commit()
        flash('New Item Added')
        return redirect(url_for('homePage'))
    else:
        return render_template('newitem.html', login_session=login_session, categories=categories)

@app.route('/<category>/<item>/edit', methods = ['GET','POST'])
def editItem(category, item):
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return redirect('/login')
    return render_template('edititem.html', login_session=login_session, categories=categories)

@app.route('/<category>/<item>/delete', methods = ['GET','POST'])
def deleteItem(category, item):
    if 'username' not in login_session:
        return redirect('/login')
    return render_template('deleteitem.html', login_session=login_session)

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


def createUser(login_session):
    newUser = User(username = login_session['username'],
        email = login_session['email'],
        image = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

def fbDisconnect():
  facebook_id = login_session['facebook_id']
  access_token = login_session['access_token']
  url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
  h = httplib2.Http()
  result = h.request(url, 'DELETE')[1]
  print(result)
  return 'You have been logged out.'




if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)