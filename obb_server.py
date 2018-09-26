from bottle import route, run, post, request, get, response
import os.path, os, hashlib, datetime, sqlite3, time, json, re, random, urllib2
from src.sessions import private
import src.auth as auth
import src.sys as sys
import src.api as api
import src.helpers as h

root_db_path = './bb/'

@post('/api/<command>/<target>')
@private
def api_route(command,target):
    try:
        data = request.json[u'data']
    except:
        message = {'messages': ['No data recieved from client'],'data': {'success': False}}
        return json.dumps(message)

    command = command.lower()

    if command == 'add':
        targets = ['board','topic','post','reply']
        if target.lower() in targets:
            message = api.add(target,data)
        else:
            message = {
                'messages': ['Invalid target: {}'.format(target)],
                'data': {'success': False}
            }
    elif command == 'list':
        targets = ['board','topic','post']
        if target.lower() in targets:
            message = api.list(target,data)
    else:
        message = {
            'messages': ['Invalid argument: {}'.format(command)],
            'data': {'success': False}
        }

    return json.dumps(message)

    opts = {
        'list': {
            'targets': ['boards','topics','posts'],
        },
        'set': {
            'targets': ['bb','topic','post'],
            'caller': None # Only used on client
        },
        'add': {
            'targets': ['board','topic','post','reply'],
        },
        'delete': {
            'targets': ['board','topic','post','reply'],
        },
        'view': {
            'targets': ['board','topic','post','user'],
        }
    }


#-#-#-#-#-#
# POST route
# command STRING - the CLI command being run
# the presence of a second param (target) will kick this
#     over to the api route
#-#-#-#-#-#
@post('/sys/<command>')
def sys_api(command):
    message = h.msg()
    try:
        data = request.json[u'data']
    except:
        message['errors'].append(1005)
        return json.dumps(message)

    user = data[u'username']
    command = command.lower()

    if command == 'logon':
        message = sys.logon(user, data)
    elif command == 'logoff':
        message = sys.logoff(user, data['token'])
    elif command == 'join':
        message = sys.join(user, data)
    elif command == 'delete':
        message = sys.delete_user(user, data['password'])
    else:
        message['errors'].append(1006)
    return json.dumps(message)


#-#-#-#-#-#
# On first run, builds the system database
# Everywhere else, use h.db_do(...), but here I chose to actually keep
#     all the queries executed/written
#-#-#-#-#-#
def check_and_build_db():
    if not os.path.isfile(root_db_path + 'sys.sqlite'):
        db_conn = sqlite3.connect(root_db_path + 'sys.sqlite')
        c = db_conn.cursor()

        c.execute("CREATE TABLE users (name text NOT NULL PRIMARY KEY, password text NOT NULL, token text DEFAULT NULL, time INTEGER NOT NULL, bio text DEFAULT NULL, contact text DEFAULT NULL, url text DEFAULT NULL)")

        c.execute("CREATE TABLE boards (name text NOT NULL PRIMARY KEY, creator text NOT NULL, time INTEGER NOT NULL, description text, private INTEGER DEFAULT 0, key text DEFAULT NULL)")

        c.execute("CREATE TABLE administration (board text NOT NULL,type text NOT NULL,value text NOT NULL, time INTEGER NOT NULL)")

        db_conn.commit()
        db_conn.close()


#-#-#-#-#-#
# Run the program
# (Build the system database if necessary)
if __name__ == '__main__':
    check_and_build_db()
    run(host='localhost', post=8080)

