import sqlite3
import dbHelper as db
from datetime import date,datetime

#db.createUsersTable()
#db.addUser('md', 'md')
#db.addTask('md', 'test2', datetime.now(), 6000)
#db.completeTask('md', 'test')

print db.getCompletedMonth('md', 5, 2018)
print datetime.now().month
#print datetime(1, 1, 1, 0, 0)
print 'done'
