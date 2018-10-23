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
home = "http://localhost:5001/"
headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
accountLoginHost = 'http://localhost:5001/ecommerce/v1/account/login'
accountDetailsHost = 'http://localhost:5001/ecommerce/v1/account/details'
accountUserHost = 'http://localhost:5001/ecommerce/v1/account/users'
removeItemsFromCartHost='http://localhost:5002/ecommerce/v1/cart/product/remove'

@app.route("/ecommerce/v1/payment/", methods=["POST"])
def payment():
#get the 'user' key
#remove all items from the 'cart'
#add items to the order table
#send user back to the root page
    s = requests.session()
    s.post(accountLoginHost, {'email':request.form['username'],'password':request.form['password']})
    resp_logIn = s.get(accountDetailsHost)
    print("response of resp_logIn=", resp_logIn.json())
    
    loggedIn = resp_logIn.json()['userInfo'][0]
    firstName = resp_logIn.json()['userInfo'][1]
    noOfItems = resp_logIn.json()['userInfo'][2]
    userId = resp_logIn.json()['userInfo'][3]
    session['email'] = resp_logIn.json()['userInfo'][4]

    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if 'email' in session:
        email = session['email']
        productsToRemoveDic = {}
        dictProducts = {}
        item = 0
        msg = ''
        
        with sqlite3.connect('ecommercedb.db') as conn:
            cur = conn.cursor()
            #get all the products in the user's cart
            #Here is where you make a network request, might need to break this down
            #get all the products in our kart
            cur.execute('SELECT products.productId, products.name, products.price, products.description, products.image FROM products INNER JOIN kart ON kart.productId = products.productId where kart.userId = ' + str(userId))
            productData = cur.fetchall()
            print("all of our products in the kart=",productData)
            for product in productData:
                #send a request to the /remove endpoint
                productsToRemoveDic.update({str(item):[str(product[0]),email,str(userId)]})
                dictProducts.update({str(item):[product[0], product[1], product[2], product[3], product[4]]})
                item = item + 1
            try:
                for k,v in dictProducts.items():
                    #Here is where you make a network request
                    cur.execute('''INSERT INTO orders (name, price, description, image, userId) VALUES (?, ?, ?, ?, ?)''', (v[1], v[2], v[3], v[4], userId))
                    conn.commit()
                for k, v in productsToRemoveDic.items():
                    print("productId=", v[0])
                    print("userId=", v[2])
                    resp = s.post(url=removeItemsFromCartHost, json={"productId":str(v[0]), "userId":str(v[2])}, headers=headers)
                    print("Result of deleting from cart=", resp.json()['response'])
                msg = "Item added successfully to the orders. Note: not necessarily deleted from cart!"
            except sqlite3.Error as e:
                print("Database error=",e)
                conn.rollback()
                msg = "Error occured"
        conn.close()
        print (msg)
    return (jsonify({'response':msg}))

if __name__ == '__main__':
    app.run(host='localhost', port=5005, debug=True,threaded=True)
