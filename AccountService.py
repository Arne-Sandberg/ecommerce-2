from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
import requests
from redissession import RedisSessionInterface

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
hostName = 'http://localhost:5003' #dynamic

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
            #Here is where you make a network request
            cur.execute("SELECT userId, firstName FROM users WHERE email = '" + session['email'] + "'")
            userId, firstName = cur.fetchone()
            resp = requests.post('http://localhost:5002/ecommerce/v1/cart/count', {'query': "SELECT count(productId) FROM kart WHERE userId = " + str(userId)} )
            noOfItems = resp.json()['response']
            print("Here is noOfItems ", noOfItems)
    conn.close()
    return jsonify({'userInfo': [loggedIn, firstName, noOfItems, userId, session['email']]})

@app.route("/ecommerce/v1/account/users", methods = ["POST"])
def category():
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
        #return render_template("login.html", error=msg)
        return jsonify({'response':msg})

@app.route("/ecommerce/v1/account/logout", methods=['GET'])
def logoutUser():
    session.pop('email', None)
    return jsonify({'response':'sucessfully logged out.'})

@app.route("/ecommerce/v1/account/password/update", methods=["GET", "POST"])
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


#-----------------------------------------------------------#
@app.route("/account/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems,_ = getUserLoginDetails()
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = '" + session['email'] + "'")
        profileData = cur.fetchone()
    conn.close()
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
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
        return render_template("changePassword.html")

@app.route("/account/updateProfile", methods=["GET", "POST"])
def updateProfile():
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
        return redirect(url_for('editProfile'))

@app.route("/account/login", methods = ["POST", "GET"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print("email=",email)
        print("password=",password)
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)

@app.route("/account/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

def is_valid(email, password):
    con = sqlite3.connect('ecommercedb.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

@app.route("/account/registerationForm")
def registrationForm():
    return render_template("register.html")

@app.route("/")
def root():
    loggedIn, firstName, noOfItems, userId = getUserLoginDetails()
    with sqlite3.connect('ecommercedb.db') as conn:
        cur = conn.cursor()
        resp_prod = requests.post('http://localhost:5003/product', {'query':"SELECT productId, name, price, description, image, stock FROM products"})
        itemData = resp_prod.json()['response']
        resp_cat = requests.post('http://localhost:5003/category', {'query': "SELECT categoryId, name FROM categories"})
        categoryData = resp_cat.json()['response']
    return render_template('home.html', itemData=parse(itemData), loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=parse(categoryData), userId=userId, hostName='http://localhost:5003' )

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
            resp_email = requests.post('http://localhost:5002/cart/itemCount', {'query': "SELECT count(productId) FROM kart WHERE userId = " + str(userId)} )
            noOfItems = resp_email.json()['response']
            print("noOfItems=", noOfItems)
            cur.execute("SELECT count(productId) FROM kart WHERE userId = " + str(userId))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems, userId)

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
    app.run(host='localhost', port=5001, debug=True,threaded=True)

#https://stackoverflow.com/questions/42879963/sharing-sessions-between-two-flask-servers
#https://gist.github.com/soheilhy/8b94347ff8336d971ad0