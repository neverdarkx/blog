from migrations.versioning import api
#from config import SQLALCHEMY_DATABASE_URI

api.upgrade('mysql://root:0611@localhost:3306/DATA')
print ( 'Current database version: ' + str(api.db_version('mysql://root:0611@localhost:3306/DATA')) )