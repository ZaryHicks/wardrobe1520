from flask import Flask, Response, render_template, request
from darksky.api import DarkSky
from darksky.types import languages, units, weather
import datetime
import json
app = Flask(__name__)


# Loads the main homepage
@app.route('/')
@app.route('/home.html')
def home():
    return render_template('home.html', page_title='Home')


# Routes to the users wardrobe
@app.route('/wardrobe.html')
def wardrobe():
	return render_template('wardrobe.html', page_title='My Wardrobe')


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
    # responseJson = json.dumps(forecast)
    # return Response(responseJson, mimetype='application/json')


    # list = [forecast.currently.time, forecast.currently.temperature, forecast.currently.apparent_temperature]

    # WHY do we get a bad gateway?
    return 'Current temperature in Pittsburgh: %s degrees' % forecast.currently.temperature


# test html form page that redirects to result.html
@app.route('/form')
def student():
    return render_template('student.html')


# from the ajax example5, index has an AJAX button that loads content by calling to /get-data
@app.route('/index.html')
def index():
    return render_template('index.html', page_title='Demo for / and /index.html')


# method called by the xmlhttp sent from index
@app.route('/get-data')
def get_data():
    responseJson = json.dumps({
        'Text': 'This content was loaded from the server.',
    })
    # we use the Response object here so that we can easily set the mimetype
    # without mimetype, some browsers may not handle the response properly.
    return Response(responseJson, mimetype='application/json')


# reults page that presents the form 
@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        req_dic = request.form.to_dict()
        print('result:{}'.format(req_dic))
        return render_template("result.html", result=req_dic)


# date page that shows the current date
@app.route('/date')
def date():
    return str(datetime.date.today())


# test of putting a variable into the path
@app.route('/hello/<name>')
def say_hello(name):
    return 'Hello %s!' % name


# test of putting an int variable into the path
@app.route('/num/<int:id>')
def number(id):
    return 'The number you entered is %d, but you already knew that' % id


if __name__ == '__main__':
    app.run(debug=True)
