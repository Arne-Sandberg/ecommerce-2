from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
services = {'products' : 'http://localhost:5000/products', 'categories': 'http://localhost:5000/categories', 'karts':'http://localhost:5000/carts'}
home = "http://localhost:80/"
hostName = 'http://localhost:80/' #dynamic
accountLoginHost = 'http://localhost:5001/ecommerce/v1/account/login'
accountDetailsHost = 'http://localhost:5001/ecommerce/v1/account/details'
accountUserHost = 'http://localhost:5001/ecommerce/v1/account/users'

@app.route("/ecommerce/v1/product/", methods=["POST"])
def addItemProduct():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = request.form['category']

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename

        with sqlite3.connect('ecommercedb.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''', (name, price, description, '', stock, categoryId))
                conn.commit()
                msg="added successfully"
            except sqlite3.Error as e:
                msg= str(e)
                conn.rollback()

        conn.close()
        return jsonify({'response':msg})

@app.route("/ecommerce/v1/product/remove", methods=['POST'])
def removeItem():
    with sqlite3.connect('ecommercedb.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM products WHERE productID = ' + str(productId['0']))
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    #return redirect(home)
    return jsonify({'response': msg})

@app.route("/ecommerce/v1/product/query", methods = ['POST'])
def product():
    query = request.form['query'] #security hazard, maybe
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        try:
            cur.execute(query)
            productData = cur.fetchall()
            msg = productData
            print(msg)
        except sqlite3.Error as e:
            conn.rollback()
            msg = str(e)
    conn.close()
    #return redirect(home)
    return jsonify({'response': msg})

@app.route("/ecommerce/v1/product/details", methods=['GET'])
def productDescriptionProduct():

    s = requests.session()
    s.post(accountLoginHost, {'email':request.form['username'],'password':request.form['password']})
    resp_logIn = s.get(accountDetailsHost)
    print("response ", resp_logIn.json())
    loggedIn = resp_logIn.json()['userInfo'][0]
    firstName = resp_logIn.json()['userInfo'][1]
    noOfItems = resp_logIn.json()['userInfo'][2]
    orderId = request.args.get('orderId') #from the orders.html
    productId = request.args.get('productId') #from the home.html
    isFromHome = False

    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        if orderId != None:
           cur.execute('SELECT products.productId, products.name, products.price, products.description, products.image, products.stock from products INNER JOIN orders ON products.name = orders.name and products.price = orders.price where orders.orderId ='+ str(orderId))
        else:
           cur.execute('SELECT products.productId, products.name, products.price, products.description, products.image, products.stock from products where products.productId='+ str(productId))
           isFromHome = True
        productData = cur.fetchone()
    conn.close()

    return jsonify({'data': productData, 'loggedIn' : loggedIn, 'firstName' : firstName, 'noOfItems' : noOfItems, 'isFromHome':isFromHome})

@app.route("/ecommerce/v1/product/category/details", methods = ['POST'])
def category():

    requery = request.form['query'] #security hazard, maybe
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        try:
            cur.execute(requery)
            productData = cur.fetchall()
            msg = productData
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    return jsonify({'response': msg})
@app.route("/ecommerce/v1/product/categories", methods=['GET'])
def displayCategoryProduct():
    s = requests.session()
    s.post(accountLoginHost, {'email':request.form['username'],'password':request.form['password']})
    resp_logIn = s.get(accountDetailsHost)
    print("response ", resp_logIn.json())
    loggedIn = resp_logIn.json()['userInfo'][0]
    firstName = resp_logIn.json()['userInfo'][1]
    noOfItems = resp_logIn.json()['userInfo'][2]
    categoryId = request.args.get("categoryId")
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = " + categoryId)
        data = cur.fetchall()
    conn.close()
    categoryName = data[0][4]
    data = parse(data)
    return jsonify({ 'data':data.pop(), 'loggedIn':loggedIn, 'firstName':firstName, 'noOfItems':noOfItems, 'categoryName':categoryName})



#-----------------------------------------------------------#
@app.route("/category/displayCategory", methods=['POST'])
def displayCategory():
    s = requests.session()
    s.post(accountLoginHost, {'email':request.form['username'],'password':request.form['password']})
    resp_logIn = s.get(accountDetailsHost)
    print("response ", resp_logIn.json())
    loggedIn = resp_logIn.json()['userInfo'][0]
    firstName = resp_logIn.json()['userInfo'][1]
    noOfItems = resp_logIn.json()['userInfo'][2]
    categoryId = request.args.get("categoryId")
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = " + categoryId)
        data = cur.fetchall()
    conn.close()
    categoryName = data[0][4]
    data = parse(data)
    return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryName=categoryName)

@app.route("/product/productDescription", methods=['POST'])
def productDescription():
    print("Entered productDescription()")
    s = requests.session()
    s.post('http://localhost:5001/account/login', {'email':request.form['username'],'password':request.form['password']})
    resp_logIn = s.get('http://localhost:5001/account/loginDetails')
    print("response ", resp_logIn.json())
    loggedIn = resp_logIn.json()['userInfo'][0]
    firstName = resp_logIn.json()['userInfo'][1]
    noOfItems = resp_logIn.json()['userInfo'][2]
    orderId = request.args.get('orderId') #from the orders.html
    productId = request.args.get('productId') #from the home.html
    isFromHome = False
    hostName = 'http://localhost:5003' #dynamic
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        if orderId != None:
           cur.execute('SELECT products.productId, products.name, products.price, products.description, products.image, products.stock from products INNER JOIN orders ON products.name = orders.name and products.price = orders.price where orders.orderId ='+ str(orderId))
        else:
           cur.execute('SELECT products.productId, products.name, products.price, products.description, products.image, products.stock from products where products.productId='+ str(productId))
           isFromHome = True
        productData = cur.fetchone()
    conn.close()
    print("Is from home.", isFromHome)
    return render_template("productDescription.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems, isFromHome = isFromHome, hostName = hostName)

@app.route("/product/add")
def admin():
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    conn.close()
    return render_template('add.html', categories=categories)
@app.route("/product/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = request.form['category']

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('ecommercedb.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''', (name, price, description, imagename, stock, categoryId))
                conn.commit()
                msg="added successfully"
            except sqlite3.Error as e:
                msg= str(e)
                conn.rollback()
        print ("Any errors=" + msg)
        conn.close()
        return redirect(home)
@app.route("/product/remove")
def remove():
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        data = cur.fetchall()
    conn.close()
    return render_template('remove.html', data=data)
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
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

#-----------------------------------------------------------#
if __name__ == '__main__':
    app.run(host='localhost', port=5003, debug=True,threaded=True)
