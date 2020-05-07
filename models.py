import psycopg2
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.username = self.getName()
        # self.userPhoto = self.getPhoto()
        self.userEmail = self.getEmail()
        self.userHeight = self.getHeight()
        self.userWeight = self.getWeight()

    def __repr__(self):
        return "%d" % self.id

    def getName(self):
        conn = MyDB()
        records = conn.query('SELECT username FROM uuser WHERE user_id = %s', (self.id,))
        return records[0][0]

    def getEmail(self):
        conn = MyDB()
        records = conn.query('SELECT email FROM uuser WHERE user_id = %s', (self.id,))
        return records[0][0]

    def getHeight(self):
        conn = MyDB()
        records = conn.query('SELECT height FROM uuser WHERE user_id = %s', (self.id,))
        return records[0][0]

    def getWeight(self):
        conn = MyDB()
        records = conn.query('SELECT weight FROM uuser WHERE user_id = %s', (self.id,))
        return records[0][0]

    def check_password(self, password):
        conn = MyDB()
        records = conn.query('SELECT ppassword FROM uuser WHERE user_id = %s', (self.id,))
        return check_password_hash(records[0][0], password)


class MyDB(object):
    def __init__(self):
        self._db_connection = psycopg2.connect(database='CouchCoach', user='postgres',
                                               password='Qwerty7', host='127.0.0.1', port='5432')
        self._db_cur = self._db_connection.cursor()

    def query(self, query, params=None):
        self._db_cur.execute(query, params)
        try:
            _db_records = self._db_cur.fetchall()
            return _db_records
        except Exception as emptyquery:
            print(emptyquery)
            return None

    def db_commit(self):
        self._db_connection.commit()

    def __del__(self):
        self._db_cur.close()
        self._db_connection.close()