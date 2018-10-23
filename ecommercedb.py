import sqlite3

#Open database using autocomit to flush out insert statements
conn = sqlite3.connect('ecommercedb.db', isolation_level=None)

#Create table
conn.execute('''CREATE TABLE users 
		(userId INTEGER PRIMARY KEY, 
		password TEXT,
		email TEXT,
		firstName TEXT,
		lastName TEXT,
		address1 TEXT,
		address2 TEXT,
		zipcode TEXT,
		city TEXT,
		state TEXT,
		country TEXT,
		phone TEXT
		)''')

conn.execute('''CREATE TABLE products
		(productId INTEGER PRIMARY KEY,
		name TEXT,
		price REAL,
		description TEXT,
		image TEXT,
		stock INTEGER,
		categoryId INTEGER,
		FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
		)''')

conn.execute('''CREATE TABLE orders
		(orderId INTEGER PRIMARY KEY,
		name TEXT,
		price REAL,
		description TEXT,
		image TEXT,
		userId INTEGER,
		FOREIGN KEY(userId) REFERENCES users(userId)
		)''')

conn.execute('''CREATE TABLE kart
		(userId INTEGER,
		productId INTEGER,
		FOREIGN KEY(userId) REFERENCES users(userId),
		FOREIGN KEY(productId) REFERENCES products(productId)
		)''')

conn.execute('''CREATE TABLE categories
		(categoryId INTEGER PRIMARY KEY,
		name TEXT
		)''')

#initial values
conn.execute('''INSERT INTO categories (categoryId, name) VALUES (1,'shoe' )''')
conn.execute('''INSERT INTO categories (categoryId, name) VALUES (2,'shirt' )''')
conn.execute('''INSERT INTO categories (categoryId, name) VALUES (3,'hat' )''')
conn.execute('''INSERT INTO categories (categoryId, name) VALUES (4,'socks' )''')

conn.close()

