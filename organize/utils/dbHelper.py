'''
todo:
- make stuff not crash when duplicate tasks are entered
- add timeDifference to tasks table
'''

import sqlite3
from datetime import datetime

'''
IMPORTANT NOTES:
-    if you make your own db modify functions, make sure to enter strings as '"text"' instead of just 'text'
-    the functions I've written work with normal strings as arguments though, so don't pass '"text"' into them
-    always save and close db at the end if you add any new db modification functions
'''

dbPath = 'data/db.db'

def switchDb(path):
    global dbPath
    dbPath = path

def openDb():
    db = sqlite3.connect(dbPath, detect_types = sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    return db

def getCursor(db):
    c = db.cursor()
    return c

def saveDb(db):
    db.commit()

def closeDb(db):
    db.close()

#run once, creates the table
#example: createTable('users', [ ['username', 'TEXT PRIMARY KEY'], ['password', 'TEXT'] ])
def createTable(tableName, columns):
    db = openDb()
    cursor = getCursor(db)
    cmdString = 'CREATE TABLE IF NOT EXISTS ' + str(tableName) + '('
    
    for column in columns:
        cmdString += str(column[0]) + ' ' + str(column[1]) + ', '
        
    #to get rid of the extra ', ' at the end
    cmdString = cmdString[:-2]
    cmdString += ');'
    
    #print cmdString
    cursor.execute(cmdString)
    saveDb(db)
    closeDb(db)

#inserts row data into a table
#example: insertRow('users', ['username', 'password'], ['"md"', '"pw"'])
def insertRow(tableName, columns, values):
    db = openDb()
    cursor = getCursor(db)
    
    cmdString = 'INSERT INTO '
    cmdString += str(tableName) + ' ('
    
    for column in columns:
        cmdString += str(column) + ', '
        
    #to get rid of the extra ', ' at the end
    cmdString = cmdString[:-2]
    cmdString += ') VALUES ('
    
    for value in values:
        cmdString += str(value) + ', '
        
    #to get rid of the extra ', ' at the end
    cmdString = cmdString[:-2]
    cmdString += ');'
    
    #print cmdString
    cursor.execute(cmdString)
    saveDb(db)
    closeDb(db)

#given a username and password, will return true if the two correspond, false otherwise
def validateLogin(username, password):
    db = openDb()
    cursor = getCursor(db)
    cmdString = 'SELECT password FROM users WHERE username = "%s";' % (username,)
    passwords = cursor.execute(cmdString).fetchone()
    
    closeDb(db)
    #print passwords
    
    if passwords == None:
        return False
        
    return passwords[0] == password
    

#returns True if a username is registered, False otherwise
def userExists(username):
    db = openDb()
    cursor = getCursor(db)
    cmdString = 'SELECT username FROM users WHERE username = "%s";' % (username,)
    usernames = cursor.execute(cmdString).fetchone()
    #print usernames
    
    closeDb(db)
    
    return usernames != None

#adds a new user. adds their login info to users table, and makes a new unique table for their tasks
def addUser(username, password):
    createTable(username, [['task', 'TEXT PRIMARY KEY'], ['startTime', 'TIMESTAMP'], ['endTime', 'TIMESTAMP'], ['expectedTime', 'INTEGER'], ['actualTime', 'REAL']])
    createTable(username+"Shopping", [['item', 'TEXT']])
    
    db = openDb()
    cursor = getCursor(db)
    insertUser = "INSERT INTO users (username, password) VALUES ('%s', '%s');" % (username, password)
    cursor.execute(insertUser)
    
    saveDb(db)
    closeDb(db)

#creates the table of usernames and passwords
def createUsersTable():
    createTable('users', [['username', 'TEXT PRIMARY KEY'], ['password', 'TEXT']])
    
#adds a task to a specific user's task table. the endTime and actualTime columns are set to -1 because they're determined on task completion, not creation
def addTask(username, task, startTime, expectedTime):
    db = openDb()
    cursor = getCursor(db)
    
    cursor.execute('INSERT INTO ' + username + ' VALUES (?, ?, ?, ?, ?)', (task, startTime, '-1', expectedTime, '-1'))

    saveDb(db)
    closeDb(db)

def completeTask(username, task):
    db = openDb()
    cursor = getCursor(db)
    
    currentTime = datetime.now()
    cursor.execute('SELECT startTime FROM %s WHERE task = ?' % (username), (task,))
    actualTime = currentTime - cursor.fetchone()[0]
    actualTime = actualTime.seconds/60.0
    
    cursor.execute('UPDATE ' + username + ' SET endTime = ?, actualTime = ? WHERE task = ?', (datetime.now(), actualTime, task))

    saveDb(db)
    closeDb(db)

# adds an item to be shopped by a user to their own shopping table
def addShop(username, item):
    db = openDb()
    cursor = getCursor(db)

    # INSERT INTO margaretShopping VALUES 'cat food'
    cursor.execute('INSERT INTO ' + username + 'Shopping VALUES (?)', (item,))

    saveDb(db)
    closeDb(db)

def completeShop(username, item):
    db = openDb()
    cursor = getCursor(db)

    # DELETE FROM margaretShopping WHERE item = 'cat food'
    cursor.execute('DELETE FROM ' + username + "Shopping WHERE item = ?", item)

    saveDb(db)
    closeDb(db)

def getItems(username):
    db = openDb()
    cursor = getCursor(db)

    # SELECT * FROM margaretShopping
    # gets everything from margaret's shopping list
    items = cursor.execute("SELECT * FROM " + username + "Shopping").fetchall()
    print items
    print "those were the items"
    return items