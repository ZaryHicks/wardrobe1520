from flask import Flask, render_template, request
import datetime
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/form')
def student():
   return render_template('student.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':

      req_dic = request.form.to_dict()

      print('result:{}'.format(req_dic))
      return render_template("result.html", result = req_dic )

@app.route('/memes')
def memes():
	return 'Wow you found the secret memes page, great work!'

@app.route('/date')
def date():
	return str(datetime.date.today())
	
@app.route('/hello/<name>')
def say_hello(name):
	return 'Hello %s!' % name

@app.route('/num/<int:id>')
def number(id):
	return 'The number you entered is %d, but you already knew that' % id


if __name__ == '__main__':
    app.run(debug = True)
