import flask
# Darksky API
from darksky.api import DarkSky
from darksky.types import languages, units, weather

from email.utils import parseaddr
import datastoreHelper
import dataClasses
import hashlib
import json


latitude = 40.443864
longitude = -79.955423


app = flask.Flask(__name__)
# No clue what this is but we need it for flask sessions?
app.secret_key = b'oaijrwoizsdfmnvoiajw34foinmzsdv98j234'

# week 6 project 9 is really good for getting us setup with 
# datastore, login, sessions


# Main homepage - do we need to expand this for differing the main page based on session? Might just go in the html
# @app.route('/')
# @app.route('/home')
# def root():
#     return show_page('home.html', 'Home')

# TRYING OTHER HOMEPAGE (for not signed in users only possibly), WE CAN DECIDE IF WE LIKE THIS
@app.route('/')
@app.route('/welcome')
def root():
    return show_page('welcome.html', 'Welcome')

# route to recommendations page NOT USED
# @app.route('/recommendations')
# def recommmend():
#     return show_page('recommendations.html', 'Recommend Clothing')


# route to sign up page
@app.route('/signup')
def signup():
    return show_page('signup.html', 'Sign Up')


# processes user registration from sign up page
@app.route('/registerUser', methods=['POST'])
def register_user():
    # from the signup form - get username, pass1/2, email
    username = flask.request.form.get('username')
    firstname = flask.request.form.get('firstname')
    password1 = flask.request.form.get('password1')
    password2 = flask.request.form.get('password2')
    email = flask.request.form.get('email')
    errors = []

    # if passes don't match - this is an error
    if password1 != password2:
        errors.append('Passwords do not match.')

    # if email is entered invalid - this is an error
    email_parts = parseaddr(email)
    if len(email_parts) != 2 or not email_parts[1]:
        errors.append('Invalid email address: ' + str(email))

    # use the entered info to create a user object
    user = dataClasses.User(username, firstname, email)

    # if there were any errors in the form - we will return them to the signup and tell them
    if errors:
        return show_page('/signup.html', 'Sign Up', errors=errors)
    else: # else if there are no erorrs, hash password, and write the user to the db
        passwordhash = hash_password(password1)

        # store User and hashed pasword into the datastore
        datastoreHelper.save_user(user, passwordhash)

        # set the session user
        flask.session['user'] = user.username
        return flask.redirect('/')


# route to sign in page
@app.route('/signin')
def signin():
    return show_page('signin.html', 'Sign In')


# processes login attempt from sign in form
@app.route('/login', methods=['POST'])
def login():
    # from the sign in form, get username and password
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')

    # hash the password
    passwordhash = hash_password(password)

    # try to get a user object from the datastore with this username and hashpass
    user = datastoreHelper.load_user(username, passwordhash)

    if user: # if we get a real user, this user is logged in, set the session user
        flask.session['user'] = user.username
        return flask.redirect('/')
    else: # if user is not real, return them to login
        errors = ['Failed to log in']
        return show_page('signin.html', 'Sign In', errors)


# route for G login --- Work glogin into sign in if we can / want glogin
@app.route('/glogin')
def gotoGlogin():
    return show_page('glogin.html', 'Login')


# signs out the user, setting their session to None and redirecting to the home page
@app.route('/signout')
def signout():
    flask.session['user'] = None
    return flask.redirect('/')


# Routes the user to their wardrobe page
@app.route('/wardrobe')
def wardrobe():
    return show_page('wardrobe.html', 'My Wardrobe')


# test page that just gives the current temperature for Pitt
@app.route('/w')
def weth():
    API_KEY = 'dac2d4024a375dc5ca6fbef64ee00428'
    darksky = DarkSky(API_KEY)
    # Harcode Pittsburgh for right now
    forecast = darksky.get_forecast(
        latitude, longitude,
        extend=False,  # default `False`
        lang=languages.ENGLISH,  # default `ENGLISH`
        values_units=units.AUTO,  # default `auto`
        exclude=[weather.MINUTELY, weather.DAILY, weather.ALERTS]  # exlclude minute/daily/alerts, we want to grab only what we need
    )
    # this does not work - we might have to construct a custom object/dict from this in terms of a string and send that?
    # might make an intermediate class that we can use to make these weather classes able to be written to json
    # responseJson = json.dumps(forecast)
    # return Response(responseJson, mimetype='application/json')
    # [forecast.currently.time, forecast.currently.temperature, forecast.currently.apparent_temperature]
    print(latitude)
    print(longitude)
    return 'Current temperature is: %s degrees' % forecast.currently.temperature


# method to receive the coordinates from the client
@app.route('/coordinates', methods=['POST'])
def getcoords():
    data = flask.request.get_json()
    global latitude
    latitude = data['lat']
    global longitude
    longitude = data['lon']
    print(data['lat'])
    print(data['lon'])
    return flask.jsonify({'result': 'Success!', 'lat': latitude, 'lon': longitude})


# from the ajax example5, index has an AJAX button that loads content by calling to /get-data
@app.route('/index')
def index():
    return show_page('index.html', 'Ajax Example')


# method called by the xmlhttp sent from index -- Ajax Example
@app.route('/get-data')
def get_data():
    responseJson = json.dumps({
        'Text': 'This content was loaded from the server.',
    })
    # we use the Response object here so that we can easily set the mimetype
    # without mimetype, some browsers may not handle the response properly.
    return flask.Response(responseJson, mimetype='application/json')


# method used to add to the wardrobe
@app.route('/add', methods=['POST'])
def add_item():
    typer = flask.request.form.get('type')
    name = flask.request.form.get('name')
    color = flask.request.form.get('color')
    casual = flask.request.form.get('casual')
    high = flask.request.form.get('high')
    low = flask.request.form.get('low')

    # now consctruct the item
    # item = dataClasses.Clothing(typer, name, color, casual, high, low)

    # store the item in the datastore in the under this user
    # datastoreHelper.save_item(get_user(), item)
    # return flask.redirect('/wardrobe')
    responseJson = json.dumps({
        'type': typer,
        'name': name,
        'color': color,
        'casual': casual,
        'high': high,
        'low': low
    })
    return flask.Response(responseJson, mimetype='application/json')


# method to remove an item from the wardrobe
@app.route('/remove', methods=['POST'])
def remove_item():
    return flask.redirect('/wardrobe')


# when a user signs in, the username is in the session[user], so we can get it at any time
def get_user():
    return flask.session.get('user', None)


# adapted from week6p9, show page is a wrapper for render_template, it allows us to easily specify what we pass to the template
def show_page(page, title, show=True, errors=None):
    # removed a lot of the show page fields, and thus the render fields
    # as we decide what needs to be passed to templates, we will add back in with this
    # same format

    # always need a page, page title, and user to pass into template
    # show? - also, does errors work?
    # errors is an array of error strings, to be displayed in the errors field in the event of errors *note: errors*
    return flask.render_template(page, page_title=title, user=get_user(), show=show, errors=errors)


# Hashes the password using sha256 from hashlib
def hash_password(pw):
    encoded = pw.encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
