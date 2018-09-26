import sqlite3, time
from bottle import request, get, post, response
from functools import wraps
import api

def private(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        data = request.json[u'data']
        token = data['token']
        user = data['user']
        db_path = './bb/sys.sqlite'
        current = int(time.time())

        db_conn = sqlite3.connect(db_path)
        c = db_conn.cursor()

        c.execute('''SELECT time FROM users WHERE name = ? and token = ?''',(user,token))
        session = c.fetchone() #this may not work if there is no data....clean up

        if session and current - int(session[0]) <= 7200:
            c.execute('''UPDATE users SET time = ? WHERE name = ? and token = ?''',(current,user,token))
            db_conn.commit()
            db_conn.close()
            return f(*args, **kwargs)
        db_conn.close()
        return {'messages': ['You are not logged in, or your session is expired','Please log in again'],'data': {'success': False}}
    return wrapper
