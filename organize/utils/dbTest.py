import dbHelper as data

data.switchDb('../data/db.db')

data.createTable('users', [['username', 'TEXT PRIMARY KEY'], ['password', 'TEXT']])
#data.insertRow('users', ['username', 'password'], ['"md"', '"pw"'])
print data.userExists('md')
print data.validateLogin('mds', 'pwd')
data.addUser('md2', 'pw')
print data.userExists('md2')
print 'done'
