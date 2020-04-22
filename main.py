import flask
from flask import request
# Darksky API
from darksky.api import DarkSky
from darksky.types import languages, units, weather
import googlemaps
from email.utils import parseaddr
import datastoreHelper
import dataClasses
import hashlib
import json


GKey = "AIzaSyAPp6UgeRBiEu0HibhtXqONS_Qf97b-S3Y"


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
    else:  # else if there are no erorrs, hash password, and write the user to the db
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

    if user:  # if we get a real user, this user is logged in, set the session user
        flask.session['user'] = user.username
        return flask.redirect('/')
    else:  # if user is not real, return them to login
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


# Shows a profile page - we can decide what goes in here? let the user update their profile info?
@app.route('/profile')
def profile():
    return show_page('profile.html', 'My Profile')

# test page that just gives the current temperature for Pitt
@app.route('/w')
def weth():
    API_KEY = 'dac2d4024a375dc5ca6fbef64ee00428'
    darksky = DarkSky(API_KEY)
    # Harcode Pittsburgh for right now
    latitude = 40.443864
    longitude = -79.955423
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
    return 'Current temperature is: %s degrees' % forecast.currently.temperature


def tempF(latitude, longitude):
    API_KEY = 'dac2d4024a375dc5ca6fbef64ee00428'
    darksky = DarkSky(API_KEY)
    forecast = darksky.get_forecast(
        latitude, longitude,
        extend=False,  # default `False`
        lang=languages.ENGLISH,  # default `ENGLISH`
        values_units=units.AUTO,  # default `auto`
        exclude=[weather.MINUTELY, weather.DAILY, weather.ALERTS]
    )
    return '%s°F' % round(forecast.currently.temperature)


def getLocation(latitude, longitude):
    gmaps = googlemaps.Client(key=GKey)
    locations = gmaps.reverse_geocode((latitude, longitude))
    city = None
    state = None
    if locations:
        for i in locations[0]['address_components']:
            for j in i['types']:
                if (j == 'locality'):
                    city = i['long_name']
                    break
        for i in locations[0]['address_components']:
            for j in i['types']:
                if (j == 'administrative_area_level_1'):
                    state = i['short_name']
                    break

        return ("%s," % city + " %s" % state)
    else:
        return "Unknown"


# method to receive the coordinates from the client
@app.route('/coordinates', methods=['POST'])
def getcoords():
    data = flask.request.get_json()
    # print(data['lat'] is not None)
    # print(data['lat'])
    latitude = 40.443864
    longitude = -79.955423
    if data['lat'] is not None and data['lon'] is not None:
        latitude = data['lat']
        longitude = data['lon']
    return tempF(latitude, longitude)+":"+getLocation(latitude, longitude)


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


# call from /wardrobe that gets user wardrobe json and returns it to populate the table
@app.route('/get_wardrobe')
def get_wardrobe():
    return datastoreHelper.get_wardrobe(get_user())


# method used to add to the wardrobe
@app.route('/add', methods=['POST'])
def add_item():
    typer = flask.request.form.get('type')
    name = flask.request.form.get('name')
    color = flask.request.form.get('color')
    casual = flask.request.form.get('casual')
    high = flask.request.form.get('high')
    low = flask.request.form.get('low')
    tags = flask.request.form.get('tags-input')

    item = dataClasses.Clothing(typer, name, color, casual, high, low, tags)

    # Get the user's wardrobe from the table, create this clothing item, add it to the list, write to datastore
    # is there a quick way to just add this onto the end of the existing array????
    datastoreHelper.add_item(get_user(), item)

    responseJson = json.dumps({
        'type': typer,
        'name': name,
        'color': color,
        'casual': casual,
        'high': high,
        'low': low
    })

    # SO: When add is called, they submitted their form, we need to add this object to their wardrobe in datastore, and then reshow the page
    # reshowing the page should add the item to the table (when the table populates from json that we fetch from datastore)
    # return flask.Response(responseJson, mimetype='application/json')

    # print the information that they submitted
    # print(responseJson)
    return flask.redirect('/wardrobe')


# method used to add to the wardrobe
@app.route('/edit', methods=['POST'])
def edit_item():
    ident = flask.request.form.get('id')
    typer = flask.request.form.get('type')
    name = flask.request.form.get('name')
    color = flask.request.form.get('color')
    casual = flask.request.form.get('casual')
    high = flask.request.form.get('high')
    low = flask.request.form.get('low')
    tags = flask.request.form.get('tags-input')

    item = dataClasses.Clothing(typer, name, color, casual, high, low, tags)
    print("Got ", item)
    # Get the user's wardrobe from the table, create this clothing item, add it to the list, write to datastore
    # is there a quick way to just add this onto the end of the existing array????
    datastoreHelper.edit_item(get_user(), item, ident)

    return flask.redirect('/wardrobe')


# method to remove an item from the wardrobe
@app.route('/remove', methods=['POST'])
def remove_item():
    data = request.json
    datastoreHelper.delete_item(get_user(), data)
    return flask.redirect('/wardrobe')


# when a user signs in, the username is in the session[user], so we can get it at any time
def get_user():
    return flask.session.get('user', None)


# method to generate outfits
@app.route('/generate', methods=['POST'])
def get_outfits():
    form = json.loads(request.data)
    isCasual = form['casual-generate']
    temp = int(form['temp-generate'])

    # isCasual = 'True'
    includeJacket = True
    includeShirts = True
    includePants = True
    includeShoes = True
    hardInclude = False
    # temp = 45
    outfits = []
    if temp is not None:
        user = get_user()
        wardrobeTable = json.loads(datastoreHelper.get_wardrobe(user))
        jackets = []
        shirts = []
        pants = []
        shoes = []
        for i in wardrobeTable:
            if i['type'] == 'Jacket':
                jackets.append(i)
            elif i['type'] == 'Shirt':
                shirts.append(i)
            elif i['type'] == 'Pants':
                pants.append(i)
            elif i['type'] == 'Shoes':
                shoes.append(i)

        useableJacket = []
        useableShirts = []
        useablePants = []
        useableShoes = []

        if includeJacket:
            for i in jackets:
                if int(i['high_temp']) >= temp and int(i['low_temp']) <= temp and i['is_casual'] == isCasual:
                    useableJacket.append(i)
        if includeShirts:
            for i in shirts:
                if int(i['high_temp']) >= temp and int(i['low_temp']) <= temp and i['is_casual'] == isCasual:
                    useableShirts.append(i)
        if includePants:
            for i in pants:
                if int(i['high_temp']) >= temp and int(i['low_temp']) <= temp and i['is_casual'] == isCasual:
                    useablePants.append(i)

        if includeShoes:
            for i in shoes:
                if int(i['high_temp']) >= temp and int(i['low_temp']) <= temp and i['is_casual'] == isCasual:
                    useableShoes.append(i)

        if(request.values['clothes'] == 'yes'):
            return json.dumps(useableJacket + useableShirts + useablePants + useableShoes)
        else:
            if hardInclude:
                if includeJacket and useableJacket == []:
                    return None
                if includeShirts and useableShirts == []:
                    return None
                if includePants and useablePants == []:
                    return None
                if includeShoes and useableShoes == []:
                    return None

            considered = []

            if useableJacket != []:
                considered.append(useableJacket)
            if useableShirts != []:
                considered.append(useableShirts)
            if useablePants != []:
                considered.append(useablePants)
            if useableShoes != []:
                considered.append(useableShoes)
            if considered == []:
                return None
            acheck = 0
            bcheck = 0
            ccheck = 0
            dcheck = 0
            conlength = len(considered)
            print(conlength)
            while acheck < len(considered[0]):
                outfit = []
                if conlength == 1:
                    outfit.append(considered[0][acheck])
                    outfits.append(outfit)
                    acheck = acheck+1
                elif conlength == 2:
                    outfit.append(considered[0][acheck])
                    outfit.append(considered[1][bcheck])
                    outfits.append(outfit)
                    bcheck = bcheck+1
                    if bcheck >= len(considered[1]):
                        bcheck = 0
                        acheck = acheck+1
                elif conlength == 3:
                    outfit.append(considered[0][acheck])
                    outfit.append(considered[1][bcheck])
                    outfit.append(considered[2][ccheck])
                    outfits.append(outfit)
                    ccheck = ccheck+1
                    if ccheck >= len(considered[2]):
                        ccheck = 0
                        bcheck = bcheck+1
                    if bcheck >= len(considered[1]):
                        bcheck = 0
                        acheck = acheck+1
                elif conlength == 4:
                    outfit.append(considered[0][acheck])
                    outfit.append(considered[1][bcheck])
                    outfit.append(considered[2][ccheck])
                    outfits.append(outfit)
                    dcheck = dcheck+1
                    if dcheck >= len(considered[3]):
                        dcheck = 0
                        ccheck = ccheck+1
                    if ccheck >= len(considered[2]):
                        ccheck = 0
                        bcheck = bcheck+1
                    if bcheck >= len(considered[1]):
                        bcheck = 0
                        acheck = acheck+1
            print('Outfits')
            for i in outfits:
                print(i)
        # return outfits
        return json.dumps(outfits)


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
