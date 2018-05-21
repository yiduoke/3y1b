import sqlite3 #enables control of an sqlite database

def openDb(path):
    db = sqlite3.connect(path)
    return db

def getCursor(db):
    c = db.cursor()
    return c

def saveDb(db):
    db.commit()

def closeDb(db):
    db.close()

#Run once, creates the table
#example: createTable('users', [ ['username', 'TEXT PRIMARY KEY'], ['password', 'TEXT'] ])
def createTable(name, columns):
    db = sqlite3.connect(db_name)
    cursor = getCursor(db)
    cmdString = 'CREATE TABLE' + str(name) + '('
    [cmdString += str(column[0]) + ' ' + str(column[1]) for column in columns]
    cmdString += ');'
    cursor.execute(cmdString)
    saveDb(db)
    closeDb(db)

def insertRow(table, fields, values, cursor):
    parameter = ' ('

    for field in fields:
        parameter += field + ", "
    parameter = parameter[0:-2] + ") VALUES ("

    for value in values:
        val = str(value)
        if isinstance(value, basestring):
            val = "'" + val + "'"
        parameter += val + ", "
    parameter = parameter[0:-2] + ");"

    insert = "INSERT INTO " + tableName + parameter
    print "\n\n" + insert + "\n\n"

    cursor.execute(insert)

##################
## USER METHODS ##
##################

#Given a username and password, will return true if the two correspond, false otherwise
def validate_login(uname, pword):
    db = sqlite3.connect(db_name)
    c = db.cursor()
    uname = uname.replace("'", "''")
    users = c.execute("SELECT password FROM users WHERE username='%s';" % (uname,)).fetchone()
    db.close()
    if users == None:
        return False
    return users[0] == pword

#Returns True if a username is registered, False otherwise
def user_exists(username):
    db = sqlite3.connect(db_name)
    c = db.cursor()
    command = "SELECT * FROM users WHERE username = '%s';"%(username)
    result = c.execute(command).fetchone()
    db.commit()
    db.close()
    if result:
        return True 
    else:
        return False

#Adds a new record to the users table. Expects username, password, and a link to their pfp
def add_new_user(user, pw):
    db = sqlite3.connect(db_name)
    c = db.cursor()
    command = "INSERT INTO users (username, password) VALUES ('%s', '%s');"%(user, pw)
    c.execute(command)
    db.commit()
    db.close()
