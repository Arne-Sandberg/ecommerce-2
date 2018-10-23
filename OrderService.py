from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
accountLoginHost = 'http://localhost:5001/ecommerce/v1/account/login'
accountDetailsHost = 'http://localhost:5001/ecommerce/v1/account/details'
accountUserHost = 'http://localhost:5001/ecommerce/v1/account/users'

@app.route("/ecommerce/v1/order/", methods=['GET'])
def allorders():
    s = requests.session()
    s.post(accountLoginHost, {'email':request.form['username'],'password':request.form['password']})
    resp_logIn = s.get(accountDetailsHost)
    loggedIn = resp_logIn.json()['userInfo'][0]
    firstName = resp_logIn.json()['userInfo'][1]
    noOfItems = resp_logIn.json()['userInfo'][2]
    userId = resp_logIn.json()['userInfo'][3]
    session['email'] = resp_logIn.json()['userInfo'][4]
    if 'email' not in session:
        return redirect(url_for('root'))
    print("session=",session)
    print("Here is the userId=",userId)
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT orderId, name, price, description, image FROM orders where userId = ' + str(userId))
        itemData = cur.fetchall()
    orderData = parse(itemData)
    print (orderData)
    #return render_template("orders.html", orderData=orderData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)
    return jsonify({'orderData':orderData, 'loggedIn':loggedIn, 'firstName':firstName, 'noOfItems':noOfItems})
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
    app.run(host='localhost', port=5004, debug=True,threaded=True)
