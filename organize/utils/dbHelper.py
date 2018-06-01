'''
todo:
- make stuff not crash when duplicate tasks are entered
- add timeDifference to tasks table
- get list of tasks for a user
- # of tasks completed for a user for given month or year, give # for each day
- use actual num days of month, not 31
'''

import sqlite3
from datetime import datetime

'''
IMPORTANT NOTES:
-    if you make your own db modify functions, make sure to enter strings as '"text"' instead of just 'text'
-    the functions i've written work with normal strings as arguments though, so don't pass '"text"' into them
-    always save and close db at the end if you add any new db modification functions
'''

dbPath = '../data/db.db'

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
    
    db = openDb()
    cursor = getCursor(db)
    insertUser = "INSERT INTO users (username, password) VALUES ('%s', '%s');" % (username, password)
    cursor.execute(insertUser)
    
    saveDb(db)
    closeDb(db)

#creates the table of usernames and passwords
def createUsersTable():
    createTable('users', [['username', 'TEXT PRIMARY KEY'], ['password', 'TEXT']])
    
#adds a task to a specific user's task table. the endTime and actualTime columns are set to a dummy time because they're determined on task completion, not creation
def addTask(username, task, startTime, expectedTime):
    db = openDb()
    cursor = getCursor(db)
    dummyTime = datetime(1, 1, 1, 0, 0)
    
    cursor.execute('INSERT INTO ' + username + ' VALUES (?, ?, ?, ?, ?)', (task, startTime, dummyTime, expectedTime, -1))

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

'''
- # of tasks completed for a user for given month give # for each day
'''

def getNumCompleted(day, tasks):
    count = 0
    
    for task in tasks:
        if task[2].day == day:
            count += 1

    return count

def getCompletedMonth(username, month):
    db = openDb()
    cursor = getCursor(db)
    
    cursor.execute('SELECT * FROM %s WHERE actualTime != -1' % (username))
    
    tasks = cursor.fetchall()
    
    completed = dict()
    
    for i in range(32):
        completed[i] = getNumCompleted(i, tasks)

    return completed
