import os.path, sqlite3, time
import auth
import helpers as h

sys_db = './bb/sys.sqlite'

def delete_user(username,password):
    message = h.msg()
    if auth.verify_password(username,password):
        password = auth.create_password_hash(password)
        query = "DELETE FROM users WHERE name = ? and password = ?"
        qvals = (username, password)
        if h.db_do(query, qvals, sys_db):
            message['success'] = True
        else:
            message['errors'].append(1003)
    else:
        message['errors'].append(1002)
    return message


def logon(username,d):
    message = h.msg()
    valid = auth.verify_password(username,d[u'password'])
    if valid:
        new_token = auth.create_session_token(username)
        current = int(time.time())
        query = "UPDATE users SET token = ?, time = ? WHERE name = ?"
        qvals = (new_token, current, username)
        if h.db_do(query, qvals, sys_db):
            message['success'] = True
            message['token'] = new_token
        else:
            message['errors'].append(1003)
    else:
        message['errors'].append(1002)
    return message


def logoff(username, token):
    message = h.msg()
    query = "UPDATE users SET time = ? WHERE name = ? and token = ?"
    qvals = (28800, username, token)
    if h.db_do(query, qvals, sys_db):
        message['success'] = True
    else:
        message['errors'].append(1002)
    return message

def join(username, d):
    message = h.msg()
    pw = auth.create_password_hash(d[u'password'])
    now = int(time.time())
    query = 'INSERT INTO users (name, password, time, bio, contact, url) VALUES(?, ?, ?, ?, ?, ?)'
    qvals = (username, pw, now, d[u'bio'], d[u'contact'], d[u'url'])
    if h.db_do(query, qvals, sys_db):
        message['success'] = True
        message['user'] = username
    else:
        message['errors'].append(1002)
    return message


