## NOTE
##   If you plan on using SQLObject, the following should be un-commented and provides
##   a starting point for setting up your schema

from sqlobject import *
from pylons.database import PackageHub
hub = PackageHub("tasktracker")
__connection__ = hub

# You should then import your SQLObject classes
# from myclass import MyDataClass


import datetime

class Task(SQLObject):
    created = DateTimeCol(default=datetime.datetime.now)
    title = StringCol()
    text = StringCol()
    live = BoolCol(default=True)
    
    status = EnumCol(default='uncompleted', enumValues=('completed', 'uncompleted'))
    
    comments = MultipleJoin("Comment")

class Comment(SQLObject):
    date = DateTimeCol(default=datetime.datetime.now)
    user = StringCol()
    text = StringCol()
    task = ForeignKey("Task")
