from flask import Flask, flash, render_template, request, session, redirect, url_for
import urllib2, json
import sqlite3
import os
from datetime import datetime
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
        username=session["username"]
        return render_template("home.html", loggedin=isLoggedIn(), tasks=db.getUncompletedTasks(username))
    else:
        return redirect(url_for("login_page"))

@app.route('/startTask/<task>', methods=["POST"])
def startTask(task):
    task.replace('%20', '')
    username = session['username']
    print task
    db.startTask(username, task)

@app.route('/completeTask/<task>', methods=["POST"])
def completeTask(task):
    task.replace('%20', '')
    username = session['username']
    db.completeTask(username, task)

#User submits task/reminder
@app.route('/submitTask', methods=["POST"])
def submitTask():
    if isLoggedIn():
        username = session["username"]
        task = request.form["task"]
        expectedTime = request.form['taskTime'] or -1
        print type(expectedTime)
        taskType = 'NONTIMED' if expectedTime == -1 else 'TIMED'
        db.addTask(username, task, taskType, datetime(1, 1, 1, 0, 0), expectedTime)
        return render_template("submitted.html", username=username, loggedin=isLoggedIn())
    else:
        return redirect(url_for("login_page"))

@app.route('/getpythondata')
def get_python_data():
    data=[{'date':"12-Apr-18", 'tasks':5},{'date':"13-Apr-18",'tasks':6},{'date':"14-Apr-18",'tasks':5},{'date':"15-Apr-18",'tasks':1},{'date':"16-Apr-18",'tasks':5},{'date':"17-Apr-18",'tasks':6},{'date':"18-Apr-18",'tasks':15},{'date':"19-Apr-18",'tasks':6},{'date':"20-Apr-18",'tasks':5},{'date':"21-Apr-18",'tasks':6},{'date':"22-Apr-18",'tasks':5},{'date':"23-Apr-18",'tasks':6},{'date':"24-Apr-18",'tasks':5},{'date':"25-Apr-18",'tasks':6},{'date':"26-Apr-18",'tasks':5},{'date':"27-Apr-18",'tasks':6}]
    
    return json.dumps(data)

@app.route('/leaderboard')
def leaderboard():
    if isLoggedIn():
        user=session["username"]
        #taskDict=db.getCompletedMonth(user,
        #dic={1:2,2:5,3:7}
        #data=convertToList(dic,"Jan",18)
        return render_template("leaderboard.html", username=user, loggedin=isLoggedIn())
    else:
        return redirect(url_for("login_page"))

def convertToList(dictionary,month,year):
    toRet=[]
    for i in range(len(dictionary)):
        toRet.append({})
    #month should be Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec
    #year should be 2 digits
    text="-"+month+"-"+str(year)
    for j in range(1,len(dictionary)+1):
        indivDict=toRet[j-1]
        indivDict["date"]=str(j)+text
        indivDict["tasks"]=int(dictionary[j])
    return toRet
    
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
        return render_template("shopping.html", items = item_list_clean, loggedin=isLoggedIn())
    else:
        return render_template("login.html")

#User submits task/reminder
@app.route('/shopping', methods=["POST"])
def submitted_shopping():
    if isLoggedIn():
        user=session["username"]
        item=request.form['item']
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
    raw = urllib2.urlopen(api_url)
    string = raw.read()
    d = json.loads(string)

    title_list = []
    picture_list = []
    price_list = []
    url_list = []

    for i in range(5):
        title_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["title"][0])
        galleryUrl = d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["galleryURL"][0] if 'galleryURL' in d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i].keys() else 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/480px-No_image_available.svg.png'
        picture_list.append(galleryUrl)
        price_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["sellingStatus"][0]["convertedCurrentPrice"][0]["__value__"])
        url_list.append(d["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"][i]["viewItemURL"][0])
    
    response = json.dumps({"titles": title_list, "pictures": picture_list, "prices": price_list, "urls": url_list})
    return response

@app.route('/complete_shopping/<item>', methods = ['POST'])
def shopped(item):
    item = item.strip()
    db.completeShop(session["username"], item)
    print item
    print "that was the item supposed to be taken off"

if __name__ == "__main__":
    app.debug = True
    app.run()
