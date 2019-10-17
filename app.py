from flask import Flask, render_template, request, flash, redirect, url_for
from form import CustomerForm
from cryptography.fernet import Fernet
import sqlite3
import base64
import hashlib

key = Fernet.generate_key()
cipher_suite = Fernet(key)

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

IMAGE_EXTENSIONS = ['jpeg', 'jpg', 'png']

@app.route('/customer', methods=['GET', 'POST'])
def customer():
	error = None
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		with sqlite3.connect('database.db') as con:
			cur = con.cursor()
			cur.execute('''SELECT custEmail,custPassword, custName FROM customers WHERE custEmail = ?''', (email,))
			rows = cur.fetchall()
			for row in rows:
				print(row[0])
				print(row[1])
				pwd = row[1]
				name=row[2]
				print(hashlib.md5(password.encode()).hexdigest())
				if hashlib.md5(password.encode()).hexdigest() == pwd:
					return redirect(url_for('customer_home', name=name))
	return render_template('customer_login.html', error=error)

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
	msg="DEFAULT"
	name = "NONE"
	form = CustomerForm()
   
	if request.method == 'POST':
		if form.validate() == False:
			flash('All fields are required.')
			return render_template('customer_register.html', form=form)
		else:
			name = form.Name.data
			gender = form.Gender.data
			address = form.Address.data
			city = form.City.data
			state = form.State.data
			pin = form.Pin.data
			country = form.Country.data
			code = form.Code.data
			mobile = form.Mobile.data
			email = form.Email.data
			password = form.Password.data
			encoded_password = hashlib.md5(password.encode()).hexdigest()
			# decoded_password = cipher_suite.decrypt(encoded_password)
			with sqlite3.connect('database.db') as con:
				cur = con.cursor()
				try:
					cur.execute("SELECT * FROM customers WHERE custEmail = ?", (email,))
					if cur.fetchone() is not None:
						print("Email already registered!!")
						return render_template('customer_register.html', form=form)

					else:
						cur.execute('''INSERT INTO customers (custName,custGender,custAddress,custCity,custState,custPin,custEmail,custPassword,custMobile,custCode,custCountry) VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (name,gender,address,city,state,pin,email,encoded_password, mobile,code,country))
						con.commit()
						msg = "Registered Successfully!!"
				except Exception as e:
					print(e)
					con.rollback()
					msg = "Error"
					name = "None"
			return redirect(url_for('customer_home', name=name))
	elif request.method == 'GET':
		return render_template('customer_register.html', form=form)


@app.route('/customer/home/<name>',  methods=['GET', 'POST'])
def customer_home(name):
	return render_template('home_page.html', name=name)

@app.route('/')
def homepage():
   return 'Hello World'

def printEmail(email):
	with sqlite3.conn('database.db') as conn:
		cur = conn.cursor()
		cur.execute('''SELECT custEmail from customers WHERE custEmail = ?''', email)
		rows = cur.fetchall()
		print(rows)

if __name__ == '__main__':
	app.run()