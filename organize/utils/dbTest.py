import sqlite3
import dbHelper as db
from datetime import date,datetime

#db.createUsersTable()
#db.addUser('md', 'md')
#db.addTask('md', 'finish softdev', datetime.now(), 500)
db.completeTask('md', 'finish softdev')

print 'done'
