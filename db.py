import datetime
from peewee import *
import secret

db_name_path = secret.get_app_dir() + '/db/quota_add.db'

database = SqliteDatabase(db_name_path)

class Quota_Update(Model):
    cust_fname = CharField(max_length=50)
    cust_lname = CharField(max_length=50)
    sc_account = CharField(max_length=100)
    cost_cent = CharField(max_length=12)
    work_order = CharField(max_length=30)
    quota_path = TextField()
    quota_id = TextField()
    date = DateTimeField(default=datetime.datetime.now)
    quota_before = FloatField()
    quota_after = FloatField()

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
