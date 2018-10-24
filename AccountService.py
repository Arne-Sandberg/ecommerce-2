from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
hostName = 'http://localhost:5003' #dynamic
cartCountHost = 'http://localhost:5002/ecommerce/v1/cart/count'

@app.route("/ecommerce/v1/account/details", methods=["GET"])
def getLoginDetails():
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        userId = ''
        print("session=", session)
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
            print("Did not obtain the current session")
            return jsonify({'userInfo': [loggedIn, firstName, noOfItems, userId, None]})
        else:
            loggedIn = True
            cur.execute("SELECT userId, firstName FROM users WHERE email = '" + session['email'] + "'")
            userId, firstName = cur.fetchone()
            resp = requests.post(cartCountHost, {'query': "SELECT count(productId) FROM kart WHERE userId = " + str(userId)} )
            noOfItems = resp.json()['response']
            print("Here is noOfItems ", noOfItems)
    conn.close()
    return jsonify({'userInfo': [loggedIn, firstName, noOfItems, userId, session['email']]})

@app.route("/ecommerce/v1/account/users", methods = ["POST"])
def fetchUserInformation():
    loggedIn, firstName, noOfItems, userId = getUserLoginDetails()
    requery = request.form['query'] #security hazard, maybe
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        try:
            cur.execute(requery)
            productData = cur.fetchall()
            msg = productData
            print(msg)
        except sqlite3.Error as e:
            print("Database error=",e)
            conn.rollback()
            msg = "Error occured"
    conn.close()
    return jsonify({'response': msg})

@app.route("/ecommerce/v1/account/update", methods=["GET", "POST"])
def updateProfileUser():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        with sqlite3.connect('ecommercedb.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE users SET firstName = ?, lastName = ?, address1 = ?, address2 = ?, zipcode = ?, city = ?, state = ?, country = ?, phone = ? WHERE email = ?', (firstName, lastName, address1, address2, zipcode, city, state, country, phone, email))
                    con.commit()
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return jsonify({'response':msg})

@app.route("/ecommerce/v1/account/login", methods = ['POST'])
def loginUser():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return jsonify({'response':'successful'})
        else:
            error = 'Invalid UserId / Password'
            return jsonify({'response':error})

@app.route("/ecommerce/v1/account/register", methods = ['POST'])
def register():
    if request.method == 'POST':
        #Parse form data
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']

        with sqlite3.connect('ecommercedb.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city, state, country, phone))
                con.commit()
                msg = "Registered Successfully"
            except sqlite3.Error as e:
                print(str(e))
                con.rollback()
                msg = "Error occured"
        con.close()
        return jsonify({'response':msg})

@app.route("/ecommerce/v1/account/logout", methods=['GET'])
def logoutUser():
    session.pop('email', None)
    return jsonify({'response':'sucessfully logged out.'})

@app.route("/ecommerce/v1/account/password/update", methods=["POST"])
def passwordUpdate():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('ecommercedb.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = '" + session['email'] + "'")
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
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
        return jsonify({'response':msg})

def is_valid(email, password):
    con = sqlite3.connect('ecommercedb.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False
def getUserLoginDetails():
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        userId = ''
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, firstName FROM users WHERE email = '" + session['email'] + "'")
            userId, firstName = cur.fetchone()
            resp_email = requests.post(cartCountHost, {'query': "SELECT count(productId) FROM kart WHERE userId = " + str(userId)} )
            noOfItems = resp_email.json()['response']
            print("noOfItems=", noOfItems)
            cur.execute("SELECT count(productId) FROM kart WHERE userId = " + str(userId))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems, userId)
if __name__ == '__main__':
    app.run(host='localhost', port=5001, debug=True,threaded=True)