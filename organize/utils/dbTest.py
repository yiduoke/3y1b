import sqlite3
import dbHelper as db
from datetime import date,datetime

#db.createUsersTable()
#db.addUser('md', 'md')
#db.addTask('md', 'test', 'TIMED', datetime.now(), 5)
#db.completeTask('md', 'test')
#print db.getCompletedMonth('md', 6, 2018)
print db.getUncompletedTasks('md')
print 'done'
