from flask import Flask, flash, render_template, request, session, redirect, url_for
import sqlite3
app = Flask(__name__)
import utils.users as users

#users.create_table()
app.secret_key = "THIS IS NOT SECURE"

#Returns true or false depending on whether an account is logged in.
def loggedIn():
    return "username" in session


#The home page displays useful information about our website. Accessible regardless of login status.
@app.route('/')
def home():
    return render_template('index.html', loggedin=loggedIn())

#This is the page users see. It asks for username and password.
@app.route('/account/login')
def login_page():
    if loggedIn():
        return redirect(url_for("tasks"))
    else:
        return render_template("login.html")

@app.route('/account/login/post', methods=['POST'])
def login_logic():
    uname = request.form.get("username", "")
    pword = request.form.get("password", "")
    if users.validate_login(uname, pword):
        session["username"] = uname
        return redirect(url_for("tasks"))
    else:
        flash("Wrong username or password.")
        return redirect(url_for("login_page"))

#This si the page users see when making an account. Asks for username, password & confirm, and a link to a profile picture.
@app.route('/account/create')
def join():
    if not loggedIn():
        return render_template("create.html")
    else:
        return redirect(url_for("tasks"))

#This is where the create account form leads. Not done yet.
@app.route('/account/create/post', methods=['POST'])
def joinRedirect():
    uname = request.form.get("username", "")
    pword = request.form.get("password", "")
    pass2 = request.form.get("passwordConfirm", "")
    if users.user_exists(uname):
        flash("This account name has already been taken, so please choose another.")
        return redirect(url_for("join"))
    elif pword != pass2:
        flash("Make sure you retype your password the same way in both boxes.")
        return redirect(url_for("join"))
    else:
        users.add_new_user(uname, pword)
        flash('The account "' + uname + '" has been created. Please login to confirm.')
        return redirect(url_for("login_page"))

    
@app.route("/tasks")
def tasks():
    if loggedIn():
        user=session["username"]
        return render_template("home.html", loggedin=loggedIn())
    else:
        return redirect(url_for("login_page"))

#User submits task/reminder
@app.route('/submitted', methods=["POST"])
def submitted():
    if loggedIn():
        user=session["username"]
        task=request.form["task"]
        #users.add_task(user, task) #calls db method 
        return render_template("submitted.html", username=user, loggedin=loggedIn())
    else:
        return redirect(url_for("login_page"))
    
 #Log out
@app.route('/account/logout')
def logout():
    if loggedIn():
        session.pop('username')
    return redirect(url_for('home'))

@app.route('/shopping')
def shopping():
    raw = urllib2.urlopen("https://svcs.ebay.com/services/search/FindingService/v1?OPERATION-NAME=findItemsByKeywords&SERVICE-VERSION=1.0.0&SECURITY-APPNAME=MdAbedin-test-PRD-a5d705b3d-43eeb6a2&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD&keywords=cat%20food")
    string = raw.read()
    d = json.loads(string)

    title_list = []
    picture_list = []
    price_list = []

    for i in range(6):
        title_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["title"][0])
        picture_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["galleryURL"][0])
        price_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["sellingStatus"][0]["convertedCurrentPrice"][0]["__value__"])

    return render_template("ebay.html", title_listy = title_list, picture_listy = picture_list, price_listy = price_list)
    
if __name__ == "__main__":
    app.debug = True
    app.run()
