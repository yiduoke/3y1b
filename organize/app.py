from flask import Flask, flash, render_template, request, session, redirect, url_for
import urllib2, json
import sqlite3
import os
import utils.dbHelper as db

app = Flask(__name__)
app.secret_key = os.urandom(32)

#users.create_table()
app.secret_key = "THIS IS NOT SECURE"

#Returns true or false depending on whether an account is logged in.
def isLoggedIn():
    return "username" in session

#The home page displays useful information about our website. Accessible regardless of login status.
@app.route('/')
def home():
    return render_template('index.html', loggedin=isLoggedIn())

#This is the page users see. It asks for username and password.
@app.route('/login')
def login():
    if isLoggedIn():
        return redirect(url_for("tasks"))
    else:
        return render_template("login.html")

#This is where the login form leads. On succesful login -> profile page. Otherwise back to /account/login
@app.route('/login/authenticate', methods=['POST'])
def authenticate():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    
    if db.validateLogin(username, password):
        session["username"] = username
        return redirect(url_for("tasks"))
    else:
        flash("Wrong username or password.")
        return redirect(url_for("login"))

#This is the page users see when making an account. Asks for username, password & confirm, and a link to a profile picture.
@app.route('/create')
def create():
    if isLoggedIn():
        return redirect(url_for("tasks"))
    else:
        return render_template("create.html")

#This is where the create account form leads. Not done yet.
@app.route('/create/addUser', methods=['POST'])
def addUser():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    password2 = request.form.get("passwordConfirm", "")
    pfp_url = request.form.get("pfp", "")
    
    if db.userExists(username):
        flash("This account name has already been taken, so please choose another.")
        return redirect(url_for("create"))
    elif password != password2:
        flash("Make sure you retype your password the same way in both boxes.")
        return redirect(url_for("create"))
    else:
        db.addUser(username, password)
        flash('The account "' + username + '" has been created. Please login to confirm.')
        return redirect(url_for("login"))

@app.route("/tasks")
def tasks():
    if isLoggedIn():
        user=session["username"]
        return render_template("home.html", loggedin=isLoggedIn())
    else:
        return redirect(url_for("login_page"))

#User submits task/reminder
@app.route('/submitted', methods=["POST"])
def submitted():
    if isLoggedIn():
        user=session["username"]
        task=request.form["task"]
        #db.addTask(user, task) #calls db method 
        return render_template("submitted.html", username=user, loggedin=isLoggedIn())
    else:
        return redirect(url_for("login_page"))
    
 #Log out
@app.route('/account/logout')
def logout():
    if isLoggedIn():
        session.pop('username')
        
    return redirect(url_for('home'))

@app.route('/shopping')
def shopping():
    if isLoggedIn():
        user=session["username"]
        item_list = db.getItems(session["username"])
        item_list_clean = []
        for item in item_list:
            item_list_clean.append(item[0])
        print item_list_clean
        return render_template("shopping.html", items = item_list_clean, loggedin=isLoggedIn())
    else:
        return render_template("login.html")

#User submits task/reminder
@app.route('/shopping', methods=["POST"])
def submitted_shopping():
    if isLoggedIn():
        user=session["username"]
        item=request.form['item']
        print item
        print "that was the item added"
        db.addShop(user, item) #calls db method to add shopping item

        item_list = db.getItems(session["username"])
        item_list_clean = []
        for item in item_list:
            item_list_clean.append(item[0])
        # return render_template("submitted.html", username=user, loggedin=isLoggedIn())
        return render_template("shopping.html", items = item_list_clean, loggedin=isLoggedIn())
    else:
        return redirect(url_for("login_page"))

# this is jQuery sending a shopping item to Flask and Flask sending back ebay results for that item
@app.route('/ebay/<item>', methods = ['POST'])
def ebay(item):
    item = item.strip()
    item = item.replace(" ", "%20")
    api_url = "https://svcs.ebay.com/services/search/FindingService/v1?OPERATION-NAME=findItemsByKeywords&SERVICE-VERSION=1.0.0&SECURITY-APPNAME=MdAbedin-test-PRD-a5d705b3d-43eeb6a2&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD&keywords="+item
    print "@@@"+api_url+"@@@"
    raw = urllib2.urlopen(api_url)
    string = raw.read()
    d = json.loads(string)

    title_list = []
    picture_list = []
    price_list = []
    url_list = []

    for i in range(5):
        title_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["title"][0])
        picture_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["galleryURL"][0])
        price_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["sellingStatus"][0]["convertedCurrentPrice"][0]["__value__"])
        url_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["viewItemURL"][0])
    
    response = json.dumps({"titles": title_list, "pictures": picture_list, "prices": price_list, "urls": url_list})
    print response
    print "those were the top 5 ebay results for " + item
    return response

if __name__ == "__main__":
    app.debug = True
    app.run()

# PLEASE DON'T DELETE THESE COMMENT LINES!!! I HAVE TO USE THEM LATER!!! --Yiduo
# @app.route('/shopping')
# def shopping():
#     raw = urllib2.urlopen("https://svcs.ebay.com/services/search/FindingService/v1?OPERATION-NAME=findItemsByKeywords&SERVICE-VERSION=1.0.0&SECURITY-APPNAME=MdAbedin-test-PRD-a5d705b3d-43eeb6a2&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD&keywords=cat%20food")
#     string = raw.read()
#     d = json.loads(string)

#     title_list = []
#     picture_list = []
#     price_list = []
#     url_list = []

#     for i in range(5):
#         title_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["title"][0])
#         picture_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["galleryURL"][0])
#         price_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["sellingStatus"][0]["convertedCurrentPrice"][0]["__value__"])
#         url_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["viewItemURL"][0])

#     return render_template("shopping.html", title_listy = title_list, picture_listy = picture_list, price_listy = price_list, url_listy = url_list)