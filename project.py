from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, make_response
from flask import session as login_session
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, Categories, Users, Upvotes, Tags, TagsItems, Downvotes, Comments
import os
from werkzeug.utils import secure_filename
import json, random, string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import requests
import hmac
import hashlib
import time
import math

app = Flask(__name__)

engine = create_engine('sqlite:///catalogdb.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


###Sort Functions ###

def date():
	return int(round(time.time() * 1000))

def score(ups, downs):
	return ups - downs

def hot(ups, downs, date):
	s = score(ups, downs)
	#order = math.log10(max(abs(s),1))
	if s > 0:
		sign = 1
	elif s < 0:
		sign = -1
	else:
		sign = 0	

	seconds = int(date) - 1134028003
	return (sign * s*1000 + seconds /  45000)

######

@app.route('/')
@app.route('/catalog')
def Index():
	categories = session.query(Categories).all()
	recent_items = session.query(Item).order_by(Item.hot_score.desc()).all()
	tags = session.query(Tags).limit(7).all()
	if len(recent_items) >= 10:
		recent_items = recent_items[0:10]
	return render_template('base.html', categories = categories, items = recent_items, login_session = login_session, tags = tags)

@app.route('/editprofile')
def EditProfile():
	user = session.query(Users).filter_by(id = login_session['user_id']).one()
	return render_template('editprofile.html', login_session = login_session,  academic = user.academic)

@app.route('/academic')
def Academic():
	user = session.query(Users).filter_by(id = login_session['user_id']).one()
	user.academic = True
	session.add(user)
	session.commit()
	return redirect(url_for('Index'))

@app.route('/catalog/categories')
def AllCategories():
	categories = session.query(Categories).all()
	return render_template('allcategories.html', categories = categories, login_session = login_session)

@app.route('/catalog/<int:categorie_id>')
def CategoriesPage(categorie_id):
	categorie = session.query(Categories).filter_by(id = categorie_id).one()
	items = session.query(Item).filter_by(categorie_id = categorie_id).all()
	return render_template('categoriepage.html', categorie = categorie, items = items, login_session = login_session)

@app.route('/teste')
def Teste():	
	return jsonify(session.query(Comments).all())

@app.route('/catalog/<int:categorie_id>/<int:item_id>', methods=['GET', 'POST'])
def Items(categorie_id, item_id):
	categories = session.query(Categories).all()
	item = session.query(Item).filter_by(id = item_id).one()
	upvotes = session.query(Upvotes).filter_by(item_id = item_id).all()
	nUpvotes = len(upvotes)
	tags = session.query(TagsItems).filter_by(item_id = item_id).all()
	comments = session.query(Comments).filter_by(item_id = item_id).all()
	return render_template('itempage.html', categories = categories, item = item, login_session = login_session, upvotes = nUpvotes, tags = tags, item_id = item_id, categorie_id = categorie_id, comments = comments)

@app.route('/comment/<int:categorie_id>/<int:item_id>', methods=['POST'])
def AddComment(categorie_id, item_id):
	user = session.query(Users).filter_by(id = login_session['user_id']).one()
	comment = Comments(item_id = item_id, content = request.form["content"], academic = user.academic)
	session.add(comment)
	session.commit()
	return redirect(url_for('Items', categorie_id = categorie_id, item_id = item_id))

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
				if warnings:
					return render_template('new.html', categories = categories, warnings = warnings, login_session = login_session)

				hot_score = hot(0,0, date())
				new_item = Item(name = request.form['name'], description = request.form['description'],
								categorie_id = int(request.form['categorie']), user_id = login_session['user_id'],
								author = request.form['author'], pub_year = int(request.form['pub_year']), ptype = request.form['type'],
								link = request.form['link'], hot_score = hot_score, date = date())
				session.add(new_item)
				session.commit()
				flash("New Item added")
				return redirect(url_for('Index'))
	except:
		flash("You must log in to create an item.")
		return redirect(url_for('Index'))

# LOGIN 

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# ---- PASSWORD HASH
def make_salt():
	return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s|%s' % (h, salt)

def valid_pw(name, pw, h):
	salt = h.split('|')[1]
	return h == make_pw_hash(name, pw, salt)
# ---- PASSWORD HASH

# ---- USERS FUNCTIONS
def createUser(login_session):
	new_user = Users(username = login_session['username'], email = login_session['email'],
					 picture = login_session['picture'])
	session.add(new_user)
	session.commit()
	user = session.query(Users).filter_by(email = login_session['email']).one()
	return user.id

def getUserInfo(user_id):
	user = session.query(Users).filter_by(id = user_id).one()
	return user

def gerUserID(email):
	try:
		user = session.query(Users).filter_by(email = email).one()
		return user.id
	except:
		return NoResultFound


# ---- USERS FUNCTIONS

@app.route('/signup', methods=['GET', 'POST'])
def Signup():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	if request.method == 'GET':
		return render_template("signup.html", state = state, login_session = login_session)
	else:
		username = request.form['username']
		email = request.form['email']
		password = request.form['pw']
		verify = request.form['verify']

		try:
			exist_email = session.query(Users).filter_by(email = email).one()
			flash('this email is already in use')
			return render_template("signup.html", state = state, login_session = login_session)
		except:
			if password != verify:
				flash("Passwords don't match")
				return render_template("signup.html", state = state, login_session = login_session)
			else:
				if email and password:
					password = make_pw_hash(email, password)
					new_user = Users(username = username, email = email,
									 picture = 'https://lh3.googleusercontent.com/-K0bIhug2Qoo/AAAAAAAAAAI/AAAAAAAAAAA/Cg3hXoRNip8/photo.jpg',
									 password = password, academic = False)
					session.add(new_user)
					session.commit()
					login_session['username'] = username
					login_session['picture'] = 'https://lh3.googleusercontent.com/-K0bIhug2Qoo/AAAAAAAAAAI/AAAAAAAAAAA/Cg3hXoRNip8/photo.jpg'
					login_session['email'] = email
					login_session['user_id'] = new_user.id
					return redirect(url_for('Index'))
				else:
					flash('You have to fill all inputs')
					return render_template("signup.html", state = state, login_session = login_session)

@app.route('/login', methods=['GET', 'POST'])
def Login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	if request.method == 'GET':
		return render_template("login.html", state = state, login_session = login_session)
	else:
		email = request.form['email']
		password = request.form['pw']
		if email and password:
			try:
				user = session.query(Users).filter_by(email = email).one()
				if valid_pw(email, password, user.password):
					login_session['username'] = user.username
					login_session['picture'] = user.picture
					login_session['email'] = user.email
					login_session['user_id'] = user.id
					return redirect(url_for('Index'))
				else:
					flash('Wrong password')
					return render_template("login.html", state = state, login_session = login_session)
			except:
				flash('Wrong email')
				return render_template("login.html", state = state, login_session = login_session)
		else:
			flash('You have to fill all inputs')
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

	#If there is no user with this email, creates a new user
	try:
		usr = session.query(Users).filter_by(email = login_session['email']).one()
		usr.picture = data['picture']
		usr.username = login_session['username']
		session.commit()
		login_session['user_id'] = usr.id
	except sqlalchemy.orm.exc.NoResultFound:
		login_session['user_id'] = createUser(login_session)

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	return output

@app.route('/gdisconnect')
def gdisconnect():

	try:
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

	except:
		del login_session['user_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		return redirect(url_for('Index'))
	
@app.route('/newcat', methods=['GET', 'POST'])
def NewCat():
	if request.method == 'POST':
		new_cat = Categories(name = request.form['name'])
		session.add(new_cat)
		session.commit()
		return redirect(url_for('Index'))
	else:
		return render_template('newcat.html', login_session = login_session)

@app.route('/newtag', methods=['GET', 'POST'])
def NewTag():
	if request.method == 'POST':
		new_tag = Tags(name = request.form['name'])
		session.add(new_tag)
		session.commit()
		return redirect(url_for('Index'))
	else:
		return render_template('newtag.html', login_session = login_session)

@app.route('/upvote/<int:categorie_id>/<int:item_id>')
def Up(categorie_id, item_id):
	if login_session['user_id']:
		alreadyup = session.query(Upvotes).filter_by(user_id = login_session['user_id'], item_id = item_id).all()
		if(not alreadyup):
			item = session.query(Item).filter_by(id = item_id).one()
			upvote = Upvotes(item_id = item_id, user_id = login_session['user_id'])
			session.add(upvote)
			session.commit()
			nUpvotes = len(session.query(Upvotes).filter_by(item_id = item_id).all())
			hot_score = hot(nUpvotes, 0, int(item.date))
			item.hot_score = hot_score
			session.add(item)
			session.commit()
			return redirect(url_for('Items', categorie_id = categorie_id, item_id = item_id))
	else: 
		flash("You must be logged in")
		return redirect(url_for('Items', categorie_id = categorie_id, item_id = item_id))
	return redirect(url_for('Items', categorie_id = categorie_id, item_id = item_id))

@app.route('/addcat/<int:categorie_id>/<int:item_id>', methods=['GET', 'POST'])
def AddTag(categorie_id, item_id):
	tags = session.query(Tags).all()
	if request.method == 'POST':
		tags_id = request.form['tags']
		new_ti = TagsItems(item_id = item_id, tags_id = tags_id)
		session.add(new_ti)
		session.commit()
		return redirect(url_for('Items', categorie_id = categorie_id, item_id = item_id))
	else:
		return render_template('addtag.html', login_session = login_session, tags = tags, item_id = item_id, categorie_id = categorie_id)

@app.route('/catalog/<int:categorie_id>/JSON')
def CategoriesItemJSON(categorie_id):
	try:
		categorie = session.query(Categories).filter_by(id = categorie_id).one()
		items = session.query(Item).filter_by(categorie_id = categorie_id).all()
		return jsonify(CatecorieItems=[i.serialize for i in items])
	except:
		return 'categorie not found'

@app.route('/catalog/categories/JSON')
def CategoriesJSON():
	categories = session.query(Categories).all()
	return jsonify(Categories=[i.serialize for i in categories])

@app.route('/catalog/items/JSON')
def ItemsJSON():
	categories = session.query(Item).all()
	return jsonify(Items=[i.serialize for i in categories])

@app.route('/catalog/items/<int:item_id>/JSON')
def ItemJSON(item_id):
	try:
		categories = session.query(Item).filter_by(id = item_id).one()
		return jsonify(Items=categories.serialize)
	except:
		return 'item not found'


@app.route('/database')
def Db():
	users = session.query(Users).all()
	return render_template('database.html', users=users)

if __name__ == '__main__':
	app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
	app.secret_key = 'super-secret-key'
	app.debug = True
	app.run(host='0.0.0.0', port=3000)	