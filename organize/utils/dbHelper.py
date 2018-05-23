import sqlite3

'''
IMPORTANT NOTES:
-    to enter strings into the db, you have to pass in stuff like '"text"' instead of just 'text'
-    always save and close db at the end if you add any new db modification functions
'''

dbPath = 'data/db.db'

def openDb():
    db = sqlite3.connect(dbPath)
    return db

def getCursor(db):
    cursor = db.cursor()
    return cursor

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
    cmdString = 'SELECT * FROM users WHERE username = "%s" AND password = "%s";' % (username, password)
    accounts = cursor.execute(cmdString).fetchone()
    
    closeDb(db)
    #print passwords
    
    return accounts != None
    

#returns True if a username is registered, False otherwise
def userExists(username):
    db = openDb()
    cursor = getCursor(db)
    cmdString = 'SELECT * FROM users WHERE username = "%s";' % (username,)
    accounts = cursor.execute(cmdString).fetchone()
    #print usernames
    
    closeDb(db)
    
    return accounts != None

#adds a new user
def addUser(username, password):
    db = openDb()
    cursor = getCursor(db)
    cmdString = "INSERT INTO users (username, password) VALUES ('%s', '%s');" % (username, password)
    cursor.execute(cmdString)
    saveDb(db)
    closeDb(db)
