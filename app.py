from flask import Flask, render_template
app = Flask(__name__)

@app.route('/customer')
def customer_login():
	return render_template('customer_login.html')

@app.route('/customer/home')
def customer_home():
	return render_template('customer_home.html')

@app.route('/')
def homepage():
   return 'Hello World'

if __name__ == '__main__':
	app.debug = True
	app.run()