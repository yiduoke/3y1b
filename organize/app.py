from flask import Flask, flash, render_template, request, session, redirect, url_for
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
    if isLoggedIn():
        session.pop('username')
        
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.debug = True
    app.run()
