from functools import wraps
from flask import Flask, session, redirect, render_template, request, url_for
from flask import flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import random
import string
import requests
import datetime

app = Flask(__name__)

# Connect to database
engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine

# Create database session
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# Custom error handlers
# The following was taken, almost verbatum, from the Udacity Lecture
CLIENT_ID = json.loads(
    open('/var/www/catalog/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Udacity Catalog Project"


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there is an error in the access token info then abort the process
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 50)
        response.headers['Content-Type'] = 'application/json'
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user id does not match given user"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if the user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['picture'] = data['picture']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'], picture=login_session['picture'])
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/disconnect')
def disconnect():
    if session['provider'] == 'google':
        gdisconnect()
    return redirect(url_for('logout'))


# Disconnect Google User
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(
            json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to manage items.')
            return redirect(url_for('index'))
        return func(*args, **kwargs)

    return decorated_function


# The main functions for the html pages are as follows:
@app.route('/')
@app.route('/catalog/')
def index():
    categories = db_session.query(Category).order_by(asc(Category.name))
    latest = db_session.query(Item).order_by(
        Item.created_at.desc()).limit(5).all()
    return render_template('default.html',
                           categories=categories, latest=latest)


# View Entire Category
@app.route('/catalog/<int:category_id>')
def displayCategory(category_id):
    categories = db_session.query(Category).all()
    item = db_session.query(Item).filter_by(id=category_id).one()
    category = db_session.query(Category).filter_by(id=item.category_id).one()
    for cat in categories:
        if cat.id == category_id:
            category = cat
            break
    items = db_session.query(Item).filter_by(category_id=category.id).all()
    return render_template('category.html', category=category,
                           categories=categories, items=items)


# Add New Item
@app.route('/catalog/<int:category_id>/new', methods=['POST', 'GET'])
@login_required
def createNew(category_id):
    if request.method == 'POST':
        newItem = Item(
            category_id=int(request.form['category']),
            name=request.form['name'],
            stars=request.form['stars'],
            description=request.form['description'],
            created_at=datetime.datetime.now(),
            user_id=session['user_id'])

        db_session.add(newItem)
        db_session.flush()
        db_session.commit()
        flash('Item successfully created.')
        return redirect(
            url_for('displayItem', category_id=category_id,
                    item_id=newItem.id))
    else:
        categories = db_session.query(Category).all()
        return render_template('createNew.html', categories=categories)


# Edit Item Function
@app.route('/catalog/<int:item_id>/edit', methods=['POST', 'GET'])
@login_required
def edit(item_id):
    item = db_session.query(Item).filter_by(id=item_id).one()
    category = db_session.query(Category).filter_by(
        id=item.category_id).one()
    categories = db_session.query(Category).all()
    for cat in categories:
        if cat.id == item.category_id:
            category = cat
            break

    # Other users are not allowed to edit items except the owner
    if item.user_id != session['user_id']:
        return redirect(
            url_for('displayItem', category_id=category.id,
                    item_id=item.id))

    if request.method == 'POST':
        if request.form['category']:
            item.category_id = request.form['category']
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']

        db_session.add(item)
        db_session.commit()
        flash('Item succesfully updated.')
        return redirect(
            url_for('displayItem', category_id=category.id, item_id=item.id))
    else:
        return render_template('edit.html', category=category,
                               categories=categories, item=item)


# Delete function
@app.route('/catalog/<int:item_id>/delete', methods=['POST', 'GET'])
@login_required
def delete(item_id):
    item = db_session.query(Item).filter_by(id=item_id).one()
    category = db_session.query(Category).filter_by(
        id=item.category_id).one()

    # Only the owner of a item can delete
    if item.user_id != session['user_id']:
        return redirect(
            url_for('displayItem', category_id=category.id,
                    item_id=item.id))

    if request.method == 'POST':
        db_session.delete(item)
        db_session.commit()
        flash('Item successfully deleted.')
        return redirect(
            url_for('displayCategory', category_id=category.id))
    else:
        return render_template(
            'delete.html', category=category, item=item)


# JSON Endpoint
@app.route('/json')
@app.route('/catalog/json')
def indexJSON():
    categories = db_session.query(Category).all()
    catalog = []
    for cat in categories:
        catalog.append(cat.serialize)
        items = db_session.query(Item).filter_by(category_id=cat.id).all()
        catalog[-1]['Items'] = [i.serialize for i in items]
    return jsonify(Categories=catalog)


# Edit Item
@app.route('/catalog/<int:category_id>/<item_id>')
def displayItem(category_id, item_id):
    category = db_session.query(Category).filter_by(
        id=category_id).one()
    item = db_session.query(Item).filter_by(id=item_id).one()
    return render_template(
        'displayItem.html', item=item, category=category)


# JSON Endpoint
@app.route('/catalog/<int:item_id>/JSON')
def itemJSON(item_id):
    item = db_session.query(Item).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)


if __name__ == "__main__":
    #app.secret_key = 'super secret key'
    app.run()