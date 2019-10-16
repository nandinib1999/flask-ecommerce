import sqlite3

conn = sqlite3.connect('database.db')
print("Database created successfully!!")

conn.execute('''CREATE TABLE IF NOT EXISTS customers (
	custID INT PRIMARY KEY,
	custName TEXT,
	custAddress TEXT,
	custCity TEXT,
	custState TEXT,
	custPin TEXT,
	custEmail TEXT,
	custPassword TEXT,
	custMobile TEXT,
	country TEXT
	)''')

conn.execute('''CREATE TABLE IF NOT EXISTS company(
	compID INT PRIMARY KEY,
	compName TEXT,
	compAddress TEXT,
	compCity TEXT,
	compState TEXT,
	compPin TEXT,
	compEmail TEXT,
	compPassword TEXT,
	compMobile TEXT,
	compCode TEXT,
	compCountry TEXT
	)''')
conn.execute('''CREATE TABLE IF NOT EXISTS products(
	proID INT PRIMARY KEY,
	proName TEXT,
	proQuantity INT,
	proPrice REAL,
	proBrandID INT ,
	proDescription TEXT,
	proCategoryID INT,
	proImage TEXT,
	FOREIGN KEY(proBrandID) REFERENCES company(compID),
	FOREIGN KEY(proCategoryID) REFERENCES categories(catID)
	)''')
conn.execute('''CREATE TABLE IF NOT EXISTS wishlist(
	wishUserID INT,
	wishProductID INT,
	FOREIGN KEY(wishUserID) REFERENCES customer(custID),
	FOREIGN KEY(wishProductID) REFERENCES company(compID)
	)''')
conn.execute('''CREATE TABLE IF NOT EXISTS cart(
	cartUserID INT,
	cartProductID INT,
	FOREIGN KEY(cartUserID) REFERENCES customer(custID),
	FOREIGN KEY(cartProductID) REFERENCES company(compID)
	)''')
conn.execute('''CREATE TABLE IF NOT EXISTS categories(
	catID INT PRIMARY KEY,
	catName TEXT
	)''')



print("Table created successfully!!")
conn.close()
