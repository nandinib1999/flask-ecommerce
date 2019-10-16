import sqlite3

conn = sqlite3.connect('database.db')
print("Database created successfully!!")

conn.execute('''CREATE TABLE customers (
	custID INT PRIMARY KEY,
	custName TEXT,
	custAddress TEXT,
	custCity TEXT,
	custState TEXT,
	custPin TEXT,
	custEmail TEXT,
	custMobile TEXT,
	country TEXT
	)''')
print("Table created successfully!!")
conn.close()