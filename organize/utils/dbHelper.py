'''
todo:
- make stuff not crash when duplicate tasks are entered
- fix bug where it shows start task button again after starting task and refreshing
'''

import sqlite3
from datetime import datetime
from calendar import monthrange
import os

'''
IMPORTANT NOTES:
-    if you make your own db modify functions, make sure to enter strings as '"text"' instead of just 'text'
-    the functions i've written work with normal strings as arguments though, so don't pass '"text"' into them
-    always save and close db at the end if you add any new db modification functions
'''

#path to db file from this file. should switch to os.path.dirname on droplet

dbPath = os.path.dirname(__file__) or '.'
dbPath += '/../data/db.db'

#in case we use more than one db, not likely
def switchDb(path):
    global dbPath
    dbPath = path

#opens the db
#using "detect_types = sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES" makes it so we can enter datetime objects and get back datetime objects instead of strings
def openDb():
    db = sqlite3.connect(dbPath, detect_types = sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    return db

#gets the cursor from a db
def getCursor(db):
    c = db.cursor()
    return c

#saves db
def saveDb(db):
    db.commit()

#closes db. db needs to be opened and closed in every function
def closeDb(db):
    db.close()

#run once, creates a table
#columns argument should be a list of sublists where first element is column name, 2nd element is sqlite type in string form
#example: createTable('users', [ ['username', 'TEXT PRIMARY KEY'], ['password', 'TEXT'] ])
def createTable(tableName, columns):
    db = openDb()
    cursor = getCursor(db)
    #using IF NOT EXISTS to avoid errors
    cmdString = 'CREATE TABLE IF NOT EXISTS ' + str(tableName) + '('
    
    for column in columns:
        cmdString += str(column[0]) + ' ' + str(column[1]) + ', '
        
    #to get rid of the extra ', ' at the end
    cmdString = cmdString[:-2]
    cmdString += ');'
    
    cursor.execute(cmdString)
    saveDb(db)
    closeDb(db)

#inserts row data into a table
#columns argument is a list of the columns to be entered
#values argument is a list of the corresponding values in the same order
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
    
    if passwords == None:
        return False
        
    return passwords[0] == password
    
#returns True if a username is registered, False otherwise
def userExists(username):
    db = openDb()
    cursor = getCursor(db)
    cmdString = 'SELECT username FROM users WHERE username = "%s";' % (username,)
    usernames = cursor.execute(cmdString).fetchone()
    
    closeDb(db)
    
    return usernames != None

#adds a new user. adds their login info to users table, and makes a new unique table for their tasks
def addUser(username, password):
    createTable(username, [['task', 'TEXT PRIMARY KEY'], ['taskType', 'TEXT'], ['startTime', 'TIMESTAMP'], ['endTime', 'TIMESTAMP'], ['expectedTime', 'INTEGER'], ['actualTime', 'REAL'], ['timeDifference', 'REAL']])
    createTable(username+"Shopping", [['item', 'TEXT PRIMARY KEY']])
    db = openDb()
    cursor = getCursor(db)
    insertUser = "INSERT INTO users (username, password) VALUES ('%s', '%s');" % (username, password)
    cursor.execute(insertUser)
    
    saveDb(db)
    closeDb(db)

#creates the table of usernames and passwords
def createUsersTable():
    createTable('users', [['username', 'TEXT PRIMARY KEY'], ['password', 'TEXT']])
    
#adds a task to a specific user's task table. the endTime, actualTime, and timeDifference columns are set to a dummy time because they're determined on task completion, not creation
#there are two taskTypes: 'TIMED' and 'NONTIMED'
#all time deltas are in minutes
def addTask(username, task, taskType, startTime, expectedTime):
    db = openDb()
    cursor = getCursor(db)
    dummyTime = datetime(1, 1, 1, 0, 0)
    
    duplicates = cursor.execute('SELECT task FROM ' + username + ' WHERE task = ?;', (task,)).fetchone()
    
    if(duplicates == None):
        cursor.execute('INSERT INTO ' + username + ' VALUES (?, ?, ?, ?, ?, ?, ?)', (task, taskType, startTime, dummyTime, expectedTime, -1, -1))
        
    saveDb(db)
    closeDb(db)

def startTask(username, task):
    db = openDb()
    cursor = getCursor(db)
    
    cursor.execute('UPDATE ' + username + ' SET startTime = ? WHERE task = ?', (datetime.now(), task))
    
    saveDb(db)
    closeDb(db)

#completes a given task for a user, uses datetime.now() as the recorded completion time
#if the task was a nontimed task, it'll still add the completion time info, but won't be used later
def completeTask(username, task):
    db = openDb()
    cursor = getCursor(db)
    
    currentTime = datetime.now()
    cursor.execute('SELECT startTime FROM %s WHERE task = ?' % (username), (task,))
    actualTime = currentTime - cursor.fetchone()[0]
    actualTime = actualTime.seconds/60.0
    cursor.execute('SELECT expectedTime FROM %s WHERE task = ?' % (username), (task,))
    timeDifference = cursor.fetchone()[0] - actualTime
    
    cursor.execute('UPDATE ' + username + ' SET endTime = ?, actualTime = ?, timeDifference = ? WHERE task = ?', (datetime.now(), actualTime, timeDifference, task))

    saveDb(db)
    closeDb(db)

#returns a dict where keys are the day # for each day in a month, and values are # of completed tasks that day for a given user. completed tasks include timed and nontimed
def getCompletedMonth(username, month, year):
    db = openDb()
    cursor = getCursor(db)
    
    cursor.execute('SELECT * FROM %s WHERE actualTime != -1' % (username))
    
    tasks = cursor.fetchall()
    
    completed = dict()
    
    numDays = monthrange(year, month)[1]
    
    for i in range(1, numDays+1):
        completed[i] = getNumCompleted(i, tasks)

    return completed

#helper fxn for getCompletedMonth(), returns # of tasks completed on a given day for a given list of tasks
def getNumCompleted(day, tasks):
    count = 0
    
    for task in tasks:
        if task[3].day == day:
            count += 1

    return count

#returns a list of the tasks a given user hasn't completed yet
def getUncompletedTasks(username):
    db = openDb()
    cursor = getCursor(db)
    
    cursor.execute('SELECT task FROM %s WHERE timeDifference = -1 ORDER BY startTime ASC' % (username))
    
    return [i[0] for i in cursor.fetchall()]
    
#returns the progress data for a given task of a given user
def getProgress(username, task):
    db = openDb()
    cursor = getCursor(db)
    
    cursor.execute('SELECT startTime, expectedTime FROM ' + username + ' WHERE task = ?', (task,))
    
    progress = cursor.fetchone()
    elapsedTimeDelta = (datetime.now()-progress[0])
    elapsedTime = (elapsedTimeDelta.seconds + (elapsedTimeDelta.microseconds/10000)/100.0)
    expectedTime = progress[1]
    percent = (elapsedTime / (expectedTime*60)) * 100 if (elapsedTime / (expectedTime*60)) < 1 else 100

    return [elapsedTime, expectedTime, percent]

def getTimes(username, task):
    db = openDb()
    cursor = getCursor(db)
    
    cursor.execute('SELECT startTime, expectedTime FROM ' + username + ' WHERE task = ?', (task,))
    
    data = cursor.fetchone()
    startTime = data[0]
    expectedTime = data[1]
    
    return [[startTime.year, startTime.month, startTime.day, startTime.hour, startTime.minute, startTime.second, startTime.microsecond/1000], expectedTime]

# adds an item to be shopped by a user to their own shopping table
def addShop(username, item):
    item = item.strip()
    db = openDb()
    cursor = getCursor(db)

    cmdString = 'SELECT item FROM ' + username + 'Shopping WHERE item = "%s";' % (item,)
    items = cursor.execute(cmdString).fetchone()

    #only add the shopping item if it doesn't already exist
    if (items == None):
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

# adds an item to be shopped by a user to their own shopping table
def addShop(username, item):
    item = item.strip()
    db = openDb()
    cursor = getCursor(db)

    cmdString = 'SELECT item FROM ' + username + 'Shopping WHERE item = "%s";' % (item,)
    items = cursor.execute(cmdString).fetchone()

    #only add the shopping item if it doesn't already exist
    if (items == None):
        # INSERT INTO margaretShopping VALUES 'cat food'
        cursor.execute('INSERT INTO ' + username + 'Shopping VALUES (?)', (item,))

    saveDb(db)
    closeDb(db)

def completeShop(username, item):
    db = openDb()
    cursor = getCursor(db)

    # DELETE FROM margaretShopping WHERE item = 'cat food'
    cursor.execute('DELETE FROM ' + username + "Shopping WHERE item = (?)", (item,))
    items = cursor.execute("SELECT * FROM " + username + "Shopping").fetchall()
    print items
    print "those were the items after completing an item..."
    
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
