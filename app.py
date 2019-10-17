from flask import Flask, render_template, request
app = Flask(__name__)

UPLOAD_FOLDER = 'static/upload'
IMAGE_EXTENSIONS = ['jpeg', 'jpg', 'png']

@app.route('/customer', methods=['GET', 'POST'])
def customer():
	error = None
	if request.method == 'POST':
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid Credentials. Please try again.'
		else:
			return "LOGGED IN"
	return render_template('customer_login.html', error=error)

@app.route('/customer/home',  methods=['GET', 'POST'])
def customer_home():
	return render_template('home_page.html')

@app.route('/')
def homepage():
   return 'Hello World'

if __name__ == '__main__':
	app.debug = True
	app.run()