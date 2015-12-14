import datetime
from peewee import *

database = SqliteDatabase('quota_add.db')

class Quota_Update(Model):
    cust_fname = CharField(max_length=50)
    cust_lname = CharField(max_length=50)
    sc_account = CharField(max_length=100)
    cost_cent = CharField(max_length=12)
    date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = database

    def setup_db():
        '''
        Setup DB table / rows if doesn't exist
        '''
        database.connect()
        database.create_tables([Quota_Update], safe=True)

    def get_transactions(request_date):
        pass

class A_User(Model):
    uname = CharField(max_length=50)

    class Meta:
        database = database

    def setup_db():
        database.connect()
        database.create_tables([A_User], safe=True)


if __name__ == "__main__":
    database.connect()
    database.create_tables([Quota_Update], safe=True)
    database.create_tables([A_User], safe=True)
