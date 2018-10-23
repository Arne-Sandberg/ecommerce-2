from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
home="http://localhost:80/"
accountLoginHost = 'http://localhost:5001/ecommerce/v1/account/login'
accountDetailsHost = 'http://localhost:5001/ecommerce/v1/account/details'
accountUserHost = 'http://localhost:5001/ecommerce/v1/account/users'

@app.route("/ecommerce/v1/cart/product", methods=["POST"])
def addProductToCart():
    s = requests.session()
    s.post(accountLoginHost, {'email':request.form['username'],'password':request.form['password']})
    resp_logIn = s.get(accountDetailsHost)

    loggedIn = resp_logIn.json()['userInfo'][0]
    firstName = resp_logIn.json()['userInfo'][1]
    noOfItems = resp_logIn.json()['userInfo'][2]
    session['email'] = resp_logIn.json()['userInfo'][4]
    msg = ''

    if 'email' not in session:
        return redirect(home+"loginForm")
    else:
        productId = request.form['productId']
        
        with sqlite3.connect('ecommercedb.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = '" + session['email'] + "'")
            userId = cur.fetchone()[0]
            try:
                if productId != None:
                    cur.execute("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, int(productId)))
                    msg = "Added successfully"
                else:
                    orderId = request.form['orderId']
                    cur.execute('SELECT products.productId from products INNER JOIN orders ON products.name = orders.name and products.price = orders.price where orders.orderId ='+ str(orderId))
                    productId = cur.fetchone()
                    print("Here is the productId=", productId)
                    if productId != None :
                        cur.execute("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, int(productId)))
                        msg = "Added successfully"
                    else:
                        msg = "Error: Cannot find productId. Nothing has been bought yet."
                conn.commit()
            except sqlite3.Error as e:
                print("Database error=",e)
                conn.rollback()
                msg = "Error occured"
        conn.close()
        return jsonify({'response':msg})

@app.route("/ecommerce/v1/cart/user", methods=["POST", "GET"])
def cartUser():
    s = requests.session()
    s.post(accountLoginHost, {'email':request.form['username'],'password':request.form['password']})
    resp_logIn = s.get(accountDetailsHost)
    
    loggedIn = resp_logIn.json()['userInfo'][0]
    firstName = resp_logIn.json()['userInfo'][1]
    noOfItems = resp_logIn.json()['userInfo'][2]
    email = resp_logIn.json()['userInfo'][4]

    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        #Here is where you make a network request to the Product/User Service to retrieve all items and category data
        resp_cat = requests.post(accountUserHost, {'query':"SELECT userId FROM users WHERE email = '" + email + "'"})
        print("response of post=",resp_cat.json()['response'][0].pop())
        userId = resp_cat.json()['response'][0].pop()
        print("Here is the userId=",str(userId))
        cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(userId))
        products = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return jsonify({'response': {'totalPrice': str(totalPrice), 'loggedIn': str(loggedIn), 'firstName': str(firstName), 'noOfItems':str(noOfItems)}})

@app.route("/ecommerce/v1/cart/product/remove", methods=["POST", "GET"])
def removeItemsFromCartCart():
    dictionary = request.get_json()

    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM kart WHERE userId = " + str(dictionary["userId"]) + " AND productId = " + str(dictionary["productId"]))
            conn.commit()
            msg = "removed successfully"
        except sqlite3.Error as e:
            print("Database error=",e)
            conn.rollback()
            msg = "Error occured"
    conn.close()
    return jsonify({'response':msg})

@app.route("/ecommerce/v1/cart/count", methods=["POST", "GET"])
def cartItems():
    with sqlite3.connect('ecommercedb.db') as conn:
        requery = request.form['query']
        cur = conn.cursor()
        cur.execute(requery)
        noOfItems = cur.fetchone()[0]
    return jsonify({'response': str(noOfItems)})

#-----------------------------------------------------------#
def removeItemsFromCart(dictionary):
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        try:
            print("here is the dictionary", dictionary)
            cur.execute("DELETE FROM kart WHERE userId = " + str(dictionary['0'][2]) + " AND productId = " + str(dictionary['0'][0]))
            conn.commit()
            msg = "removed successfully"
        except sqlite3.Error as e:
            print("Database error=",e)
            conn.rollback()
            msg = "Error occured"
    conn.close()
    print("result ", msg)
    return jsonify({'response':msg})
@app.route("/cart/checkout", methods=["POST"])
def checkout():
    if 'email' in session:
        email = session['email']
        return render_template('payment.html', loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, error='')
    else:
        return redirect(home)
@app.route("/cart/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))

    email = session['email']
    productId = int(request.args.get('productId'))
    print (removeItemsFromCart({'0':[productId,email,userId]}))
    return redirect(home)
@app.route("/cart/", methods=['POST'])
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    #if 'email' not in session:
    #    return redirect(url_for('loginForm'))
    #print("here is the session=",session)
    s = requests.session()
    s.post('http://localhost:5001/account/login', {'email':request.form['username'],'password':request.form['password']})
    resp_logIn = s.get('http://localhost:5001/account/loginDetails')
    print("response ", resp_logIn.json())
    
    loggedIn = resp_logIn.json()['userInfo'][0]
    firstName = resp_logIn.json()['userInfo'][1]
    noOfItems = resp_logIn.json()['userInfo'][2]
    email = resp_logIn.json()['userInfo'][4]
    print("First name of the user ", firstName)
    print("Here is the number of items ", noOfItems)
    print("Here is the email ", email)
   
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        #Here is where you make a network request to the Product/User Service to retrieve all items and category data
        resp_cat = requests.post('http://localhost:5001/account/users', {'query':"SELECT userId FROM users WHERE email = '" + email + "'"})
        print("response of post=",resp_cat.json()['response'][0].pop())
        userId = resp_cat.json()['response'][0].pop()
        #cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        #userId = cur.fetchone()[0]
        print("Here is the userId=",str(userId))
        cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(userId))
        products = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)
#-----------------------------------------------------------#

if __name__ == '__main__':
    app.run(host='localhost', port=5002, debug=True,threaded=True)
