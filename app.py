from flask import Flask, render_template, request, flash, redirect, url_for, session
from form import CustomerForm, CategoryForm, CompanyForm
import sqlite3
import base64
import hashlib
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

IMAGE_EXTENSIONS = ['jpeg', 'jpg', 'png']

def checkSession():
	if 'email' not in session:
		user_name = ""
		user_email = ""
		error = "Not Logged In"
		login_flag = False
	else:
		user_name = session['name']
		user_email = session['email']
		login_flag = True
	return (login_flag, user_name, user_email)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.route('/customer/logout')
def cust_logout():
	session.pop('email', None)
	return redirect(url_for('customer_home', name="None"))


@app.route('/business/logout')
def comp_logout():
	session.pop('email', None)
	return redirect(url_for('company_home', name="None"))

@app.route('/business/add/item', methods=['GET', 'POST'])
def add_item():
	error = None
	login_flag, name, email = checkSession()
	if request.method == 'POST':
		print('POST')
		if login_flag:
			print('Flag')
			item_name = request.form['name']
			qty = request.form['stock']
			price = float(request.form['price'])
			description = request.form['description']
			image = request.files['Image']
			filename = secure_filename(image.filename)
			image.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(image.filename)))
			category = request.form['category']
			sub_category = request.form['sub_category']
			name = session['name']
			with sqlite3.connect('database.db') as con:
				cur = con.cursor()
				try:
					print('Enter database')
					cur.execute('''SELECT compID from company WHERE compName = ?''', (name,))
					rows = cur.fetchone()
					print(rows[0])
					comp_id = rows[0]
					cur.execute('''SELECT catID from categories WHERE catParentName = ? AND catSubName = ?''', (category, sub_category,))
					rows = cur.fetchone()
					print(rows[0])
					cat_id = rows[0]
					cur.execute('''INSERT INTO products (proName, proQuantity, proPrice, proBrandID, proDescription, proCategoryID, proImage) VALUES (?,?,?,?,?,?,?)
						''', (item_name, qty, price, comp_id, description, cat_id, filename))
					con.commit()
					print("Added Successfully!!")
				except Exception as e:
					print(e)
					print("ERRRRR")
					error = e
					con.rollback()
			return redirect(url_for('company_home', name=name))
		else:
			redirect(url_for('business'))
	return render_template('add_items.html')



@app.route('/business/add/category', methods=['GET', 'POST'])
def add_category():
	error = None
	form = CategoryForm()
	response = checkSession()
	print(response)
	login_flag = response[0]
	name = response[1]
	email = response[2]
	if request.method == 'POST':
		print('POST')
		if login_flag: 
			print('login_flag')
			if form.validate():
				print('FormValidate')
				parent_category = form.parent_category_name.data
				category = form.category_name.data
				description = form.description.data
				try:
					with sqlite3.connect('database.db') as con:
						cur = con.cursor()
						cur.execute('''INSERT INTO categories (catParentName,catSubName,catDescription) VALUES (?,?,?)''', (parent_category, category, description))
						con.commit()
				except Exception as e:
					print('ERRRRR', e)
					error = e
					con.rollback()
				con.close()
			else: 
				print('FOrmNotValid')
				print(form.errors)
				return render_template('add_categories.html', form=form)
			return redirect(url_for('company_home', name=name))
		else:
			redirect(url_for('customer'))
	return render_template('add_categories.html', form=form)

@app.route('/business', methods=['GET', 'POST'])
def business():
	error = None
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		with sqlite3.connect('database.db') as con:
			cur = con.cursor()
			cur.execute('''SELECT compEmail,compPassword, compName FROM company WHERE compEmail = ?''', (email,))
			rows = cur.fetchall()
			for row in rows:
				print(row[0])
				print(row[1])
				email = row[0]
				pwd = row[1]
				name=row[2]
				print(hashlib.md5(password.encode()).hexdigest())
				if hashlib.md5(password.encode()).hexdigest() == pwd:
					session['email'] = email
					session['name'] = name
					return redirect(url_for('company_home', name=name))
		con.close()
	elif request.method == 'GET':
		return render_template('business_login.html', error=error)

@app.route('/business/register', methods=['GET', 'POST'])
def business_register():
	error=None
	name = "NONE"
   
	if request.method == 'POST':
		first_name = request.form['company_name']
		email = request.form['email']
		mobile = request.form['mobile']
		address = request.form['address']
		password= request.form['password']
		confirm_password = request.form['confirm']
		encoded_password = hashlib.md5(password.encode()).hexdigest()
		pin = request.form['pincode']
		city = request.form['city']
		state = request.form['state']
		code = request.form['code']
		country = request.form['country']
					# decoded_password = cipher_suite.decrypt(encoded_password)
		with sqlite3.connect('database.db') as con:
			print('Enter Database')
			cur = con.cursor()
			try:
				cur.execute("SELECT * FROM company WHERE compEmail = ?", (email,))
				if cur.fetchone() is not None:
					print("Email already registered!!")
					error = "Email already registered!!"
					return redirect(url_for('business_register', error=error))
				else:
					print('Executing INSERT Command !!')
					cur.execute('''INSERT INTO company (compName,compAddress,compCity,compState,compPin,compEmail,compPassword,compMobile,compCode,compCountry) VALUES (?,?,?,?,?,?,?,?,?,?)''', (first_name,address,city,state,pin,email,encoded_password, mobile,code,country))
					con.commit()
					error = "Registered Successfully!!"
					flash('Registered Successfully!!')
					print("Registered Successfully!!")
			except Exception as e:
				print("EERRRRRROOORRRRR", e)
				con.rollback()
				error = "Database Error"
				name = "None"
				return redirect(url_for('business_register', error=error))
		con.close()
		session['name'] = first_name
		session['email'] = email
		name = first_name
		return redirect(url_for('company_home', name=name))
	elif request.method == 'GET':
		print("GET MEthod")
		return render_template('business_signup.html')



@app.route('/customer', methods=['GET', 'POST'])
def customer():
	error = None
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		with sqlite3.connect('database.db') as con:
			cur = con.cursor()
			cur.execute('''SELECT custEmail,custPassword, custFirstName FROM customers WHERE custEmail = ?''', (email,))
			rows = cur.fetchall()
			for row in rows:
				print(row[0])
				print(row[1])
				email = row[0]
				pwd = row[1]
				name=row[2]
				print(hashlib.md5(password.encode()).hexdigest())
				if hashlib.md5(password.encode()).hexdigest() == pwd:
					session['email'] = email
					session['name'] = name
					return redirect(url_for('customer_home', name=name))
				else:
					print('Password Not Matched!!!')
					return render_template('customer_login.html', error=error)
		con.close()
	elif request.method == 'GET':
		return render_template('customer_login.html', error=error)

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
	error="DEFAULT"
	name = "NONE"
   
	if request.method == 'POST':
		first_name = request.form['first_name']
		last_name = request.form['last_name']
		gender = request.form['gender']
		email = request.form['email']
		mobile = request.form['mobile']
		address = request.form['address']
		password= request.form['password']
		confirm_password = request.form['confirm']
		encoded_password = hashlib.md5(password.encode()).hexdigest()
		pin = request.form['pincode']
		city = request.form['city']
		state = request.form['state']
		code = request.form['code']
		country = request.form['country']
		with sqlite3.connect('database.db') as con:
			cur = con.cursor()
			try:
				cur.execute("SELECT * FROM customers WHERE custEmail = ?", (email,))
				if cur.fetchone() is not None:
					print("Email already registered!!")
					return render_template('customer_register.html')

				else:
					cur.execute('''INSERT INTO customers (custfirstName,custLastName,custGender,custAddress,custCity,custState,custPin,custEmail,custPassword,custMobile,custCode,custCountry) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', (first_name,last_name,gender,address,city,state,pin,email,encoded_password, mobile,code,country))
					con.commit()
					error = "Registered Successfully!!"
			except Exception as e:
				print("EERRRRRROOORRRRR", e)
				con.rollback()
				error = "Database Error"
				name = "None"
				return redirect(url_for('customer_register', error=error))
		con.close()
		session['name'] = first_name
		session['email'] = email
		name = first_name
		return redirect(url_for('customer_home', name=first_name))
	elif request.method == 'GET':
		return render_template('customer_register.html')

@app.route("/business/displayProduct/<product_id>", methods=['GET', 'POST'])
def display_product_business(product_id):
	login_flag, name, email = checkSession()
	if not login_flag:
		return redirect(url_for(business))
	else:
		print(product_id)
		try:
			with sqlite3.connect('database.db') as conn:
				cur = conn.cursor()
				print('Fetching product data from database')
				cur.execute('''SELECT proID, proName, proPrice, proDescription, proBrandID, proImage from products where proID = (?)''', (product_id,))
				data = cur.fetchall()
				print(data)
				print('Fetching completed!!')
			return render_template('product_display.html', data=data)
		except Exception as e:
			print('EEERRRR ', e)
			conn.rollback()
	return render_template('404.html')

@app.route("/customer/displayProduct/<product_id>", methods=['GET', 'POST'])
def display_product_customer(product_id):
	login_flag, name, email = checkSession()
	if not login_flag:
		return redirect(url_for(customer))
	else:
		print(product_id)
		try:
			with sqlite3.connect('database.db') as conn:
				cur = conn.cursor()
				print('Fetching product data from database')
				cur.execute('''SELECT proID, proName, proPrice, proDescription, proBrandID, proImage from products where proID = (?)''', (product_id,))
				data = cur.fetchall()
				print(data)
				print('Fetching completed!!')
			return render_template('product_display.html', data=data)
		except Exception as e:
			print('EEERRRR ', e)
			conn.rollback()
			return render_template('404.html')


@app.route("/displayCategory/<categoryName>", methods=['GET', 'POST'])
def displayCategory(categoryName):
        login_flag, Name, email = checkSession()
        print(categoryName)
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT products.proID, products.proName, products.proQuantity, products.proPrice, products.proImage, products.proBrandID, categories.catSubName,categories.catParentName FROM products, categories WHERE categories.catID = products.proCategoryID AND categories.catParentName = (?)", (categoryName,))
            data = cur.fetchall()
        conn.close()
        # categoryName = data[0][4]
        data = parse(data)
        print("CATEGORY DATA ", data)
        return render_template('displayCategories.html', data=data, name=Name)

@app.route('/cart/add/<product_id>/<quantity>', methods=['GET', 'POST'])
def add_to_cart(product_id, quantity):
	login_flag, name, email = checkSession()
	if not login_flag:
		return redirect(url_for(customer))
	else:
		try:
			with sqlite3.connect('database.db') as conn:
				cur = conn.cursor()
				cur.execute("SELECT custID from customers where custEmail = ?", (email,))
				data = cur.fetchall()
				print(data[0][0])
				print('Adding to cart...')
				cur.execute('''INSERT INTO cartItems (cartUserID, cartProductID, cartProductQuantity) VALUES (?,?,?)''', (data[0][0],product_id,quantity,))
				conn.commit()
				print('Added Successfully!!')
			return render_template('SUCCESSS!!!!')
		except Exception as e:
			print('EEERRRR ', e)
			conn.rollback()
			return render_template('404.html')

# @app.route('/cart/view', methods=['GET', 'POST'])
# def view_cart():
# 	login_flag, name, email = checkSession()
# 	if not login_flag:
# 		return redirect(url_for(customer))
# 	else:
# 		try:
# 			with sqlite3.connect('database.db') as con:
# 				cur = con.cursor()
# 				cur.execute("SELECT custID from customers where custEmail = ?", (email,))
# 				data = cur.fetchall()
# 				print(data[0][0])
# 				cur.execute('''SELECT p.proID, p.proName, p.proPrice, comp.compName from products p, cart c, customers cus, company comp WHERE cus.custID=c.cartUserID and cus.custID=''')



@app.route('/customer/home/<name>',  methods=['GET', 'POST'])
def customer_home(name):
	login_flag, name, email = checkSession()
	with sqlite3.connect('database.db') as conn:
		cur = conn.cursor()
		cur.execute('SELECT proID, proName, proPrice, proQuantity, proDescription, proBrandID, proCategoryID, proImage FROM products')
		itemData = cur.fetchall()
		cur.execute('SELECT catID, catParentName, catSubName, catDescription FROM categories')
		categoryData = cur.fetchall()
	itemData = parse(itemData)
	#convertDict(categoryData)   
	return render_template('customer_home.html', name=name, itemData=itemData, categoryData=categoryData)

@app.route('/business/home/<name>',  methods=['GET', 'POST'])
def company_home(name):
	login_flag, name, email = checkSession()
	with sqlite3.connect('database.db') as conn:
		cur = conn.cursor()
		cur.execute('SELECT proID, proName, proPrice, proQuantity, proDescription, proBrandID, proCategoryID, proImage FROM products')
		itemData = cur.fetchall()
		cur.execute('SELECT DISTINCT catParentName FROM categories')
		categoryData = cur.fetchall()
	itemData = parse(itemData)
	#convertDict(categoryData)   
	return render_template('business_home.html', name=name, itemData=itemData, categoryData=categoryData)


#### SALONI ----------------

@app.route("/profile/<name>")
def profileHome(name):
	login_flag, name, email = checkSession()
	return render_template("home_profile.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/profile/edit/")
def editProfile():
	with sqlite3.connect('database.db') as conn:
		cur = conn.cursor()
		cur.execute("SELECT custName,custGender,custAddress,custCity,custState,custPin,custEmail,custCode, custMobile, custCountry FROM customers WHERE email = '" + session['email'] + "'")
		profileData = cur.fetchone()
		conn.close()
	return render_template("editProfile_cust.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/profile1/edit")
def editProfileCompany():
    with sqlite3.connect('database.db') as conn:
       cur = conn.cursor()
       cur.execute("SELECT compName,compAddress,compCity,compState,compPin, compEmail,compCode, compMobile,compCountry FROM company WHERE email = '" + session['email'] + "'")
       profileData = cur.fetchone()
    conn.close()
    return render_template("editProfile_comp.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/profile/changePassword", methods=["GET", "POST"])
def changePassword():
	email = request.form['email']
	password = request.form['password']
	if request.method == "POST":
	    pwd = request.form['pwd']
	    pwd = hashlib.md5(pwd.encode()).hexdigest()
	    newPwd = request.form['newpwd']
	    newPwd = hashlib.md5(newPwd.encode()).hexdigest()
	    with sqlite3.connect('database.db') as conn:
	        cur = conn.cursor()
	        cur.execute("SELECT custID, custPassword FROM customers WHERE email = '" + session['email'] + "'")
	        custID,custPassword = cur.fetchone()
	        if (password == pwd):
	            try:
	                cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPwd, userId))
	                conn.commit()
	                msg="Changed successfully"
	            except:
	                conn.rollback()
	                msg = "Failed"
	            return render_template("changePassword.html", msg=msg)
	        else:
	            msg = "Wrong password"
	    conn.close()
	    return render_template("changePassword.html", msg=msg)
	else:
	    return render_template("changePassword.html")

@app.route('/')
def homepage():
   return 'Hello World'

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

if __name__ == '__main__':
	app.run()