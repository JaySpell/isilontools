import datetime
from peewee import *

quota_db = SqliteDatabase('quota_add.db')
user_db = SqliteDatabase('user.db')

class Quotas_DB(Model):
    cust_fname = CharField(max_length=50)
    cust_lname = CharField(max_length=50)
    sc_account = CharField(max_length=100)
    cost_cent = CharField(max_length=12)
    date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = quota_db

    def setup_db():
        '''
        Setup DB table / rows if doesn't exist
        '''
        quota_db.connect()
        quota_db.create_tables([Quotas], safe=True)

    def get_transactions(request_date):
        pass

class Users_DB(Model):
    uname = CharField(max_length=50)

    class Meta:
        database = user_db

    def setup_db():
        user_db.connect()
        user_db.create_tables([Users], safe=True)


if __name__ == "__main__":
    quota_db.connect()
    quota_db.create_tables([Quotas], safe=True)
    user_db.connect()
    user_db.create_tables([Users], safe=True)
