from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, make_response
from flask import session as login_session
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, Categories, Users
import os
from werkzeug.utils import secure_filename
import json, random, string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import requests

app = Flask(__name__)

engine = create_engine('sqlite:///catalogdb.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog')
def Index():
	categories = session.query(Categories).all()
	recent_items = session.query(Item).order_by(Item.id.desc()).all()
	if len(recent_items) >= 10:
		recent_items = recent_items[0:10]
	return render_template('base.html', categories = categories, items = recent_items, login_session = login_session)

@app.route('/catalog/categories')
def AllCategories():
	categories = session.query(Categories).all()
	return render_template('allcategories.html', categories = categories, login_session = login_session)

@app.route('/catalog/<int:categorie_id>')
def CategoriesPage(categorie_id):
	categorie = session.query(Categories).filter_by(id = categorie_id).one()
	items = session.query(Item).filter_by(categorie_id = categorie_id).all()
	return render_template('categoriepage.html', categorie = categorie, items = items, login_session = login_session)

@app.route('/catalog/<int:categorie_id>/<int:item_id>')
def Items(categorie_id, item_id):
	categories = session.query(Categories).all()
	item = session.query(Item).filter_by(id = item_id).one()
	return render_template('itempage.html', categories = categories, item = item, login_session = login_session)

@app.route('/catalog/<int:item_id>/edit', methods=['GET', 'POST'])
def Edit(item_id):
	warnings = []
	item = session.query(Item).filter_by(id = item_id).one()
	try:
		if item.user.email == login_session['email']:
			categories = session.query(Categories).all()
			if request.method == 'POST':
				if not request.form['name']:
					warnings.append("You can't leave your item nameless")
					return render_template('edit.html', categories = categories, item = item, warnings = warnings, login_session = login_session)
				item.categorie_id = int(request.form['categorie'])
				item.name = request.form['name']
				item.description = request.form['description']
				session.commit()
				flash("Item edited")
				return redirect(url_for('Items', categorie_id = item.categorie_id, item_id = item.id))
			else:
				return render_template('edit.html', categories = categories, item = item, warnings = warnings, login_session = login_session)
		else:
			flash("You can't edit an Item that is not yours")
			return redirect(url_for('Items', categorie_id = item.categorie_id, item_id = item.id))
	except:
		flash("You must be logged in")
		return redirect(url_for('Items', categorie_id = item.categorie_id, item_id = item.id))
	
@app.route('/catalog/<int:item_id>/delete', methods=['GET','POST'])
def Delete(item_id):
	item = session.query(Item).filter_by(id = item_id).one()
	try:
		if login_session['email'] == item.user.email:
			if request.method == 'POST':
				session.delete(item)
				session.commit()
				flash("Item deleted")
				return redirect(url_for('Index'))
			else:
				return render_template('delete.html', item = item, login_session = login_session)
		else:
			flash("You can't delete an Item that is not yours")
			return redirect(url_for('Items', categorie_id = item.categorie_id, item_id = item.id))
	except:
		flash("You must be logged in")
		return redirect(url_for('Items', categorie_id = item.categorie_id, item_id = item.id))

UPLOAD_FOLDER = 'static/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/catalog/new', methods=['GET','POST'])
def New():
	try:
		if login_session['email']:
			warnings = []
			categories = session.query(Categories).all()
			if request.method == 'GET':
				return render_template('new.html', categories = categories, login_session = login_session)
			else:
				if not request.form['name']:
					warnings.append('You must give your item a name')
				# check if the post request has the file part
				file = request.files['file']
				# if user does not select file, browser also
				# submit a empty part without filename
				if file.filename == '':
					warnings.append('No selected file')
				if file and not allowed_file(file.filename):
					warnings.append('This fileis not allowed')
				if warnings:
					return render_template('new.html', categories = categories, warnings = warnings, login_session = login_session)

				filename = secure_filename(file.filename)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				new_item = Item(name = request.form['name'], description = request.form['description'],
								img = filename ,categorie_id = int(request.form['categorie']), user_email = login_session['email'])
				session.add(new_item)
				session.commit()
				flash("New Item added")
				return redirect(url_for('Index'))
	except:
		flash("You must log in to create an item.")
		return redirect(url_for('Index'))

# LOGIN 

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

@app.route('/login')
def Login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template("login.html", state = state, login_session = login_session)

@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	code = request.data

	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
		   % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID does not match app's."), 401)
		print "Token's client ID does not match app's."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'),
								 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	login_session['access_token'] = access_token
	login_session['credentials'] = credentials
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	if data['name']:
		login_session['username'] = data['name']
	else:
		login_session['username'] = 'unknown'
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	try:
		session.query(Users).filter_by(email = login_session['email']).one()
	except sqlalchemy.orm.exc.NoResultFound:
		new_user = Users(username = login_session['username'], email = login_session['email'],
						 picture = login_session['picture'])
		session.add(new_user)
		session.commit()

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	return output

@app.route('/gdisconnect')
def gdisconnect():
	access_token = login_session['access_token']
	print 'In gdisconnect access token is'
	print access_token
	print 'User name is: ' 
	print login_session['username']
	if access_token is None:
		print 'Access Token is None'
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
	print 'url is: %s', url
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print 'result is '
	print result
	if result['status'] == '200':
		del login_session['access_token'] 
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return redirect(url_for('Index'))
	else:
	
		response = make_response(json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response

@app.route('/newcat', methods=['GET', 'POST'])
def NewCat():
	if request.method == 'POST':
		new_cat = Categories(name = request.form['name'])
		session.add(new_cat)
		session.commit()
		return redirect(url_for('Index'))
	else:
		return render_template('newcat.html', login_session = login_session)

@app.route('/catalog/<int:categorie_id>/JSON')
def CategoriesItemJSON(categorie_id):
	categorie = session.query(Categories).filter_by(id = categorie_id).one()
	items = session.query(Item).filter_by(categorie_id = categorie_id).all()
	return jsonify(CatecorieItems=[i.serialize for i in items])

@app.route('/catalog/categories/JSON')
def CategoriesJSON():
	categories = session.query(Categories).all()
	return jsonify(Categories=[i.serialize for i in categories])


if __name__ == '__main__':
	app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
	app.secret_key = 'super-secret-key'
	app.debug = True
	app.run(host='0.0.0.0', port=3000)	