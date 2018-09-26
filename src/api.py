import os.path, sqlite3, time, re
import auth
import helpers as h

sys_db = './bb/sys.sqlite'

def add(target,d):
    message = h.msg()
    val = d[u'value']
    db_path = './bb/{}.sqlite'.format(d[u'board'])
    if target == 'board':
        if re.match(r'^[\w-]{4,20}$',val):
            finished = 0
            filepath = './bb/{}.sqlite'.format(val)
            now = time.time()
            query1 = "CREATE TABLE bb (type text NOT NULL, headline text NOT NULL, body text NOT NULL,creator text NOT NULL, parent_id, creation_time integer NOT NULL)"
            if h.db_do(query1,'',filepath):
                finished += 1
            query2 = "INSERT INTO boards (name,creator,time,description) VALUES (?,?,?,?)"
            qvals2 = (val,d[u'user'],now,d[u'body'])
            if h.db_do(query2,qvals2,sys_db):
                finished += 1
            if finished > 1:
                message['success'] = True
            else:
                message['errors'].append(1003)
        else:
            message['errors'].append(1005)
    elif target == 'topic':
        if not re.match(r'^[-\w ]{1,50}$',d[u'headline']):
            message['errors'].append(1005)
        elif not os.path.isfile(db_path):
            message['errors'].append(1001)
        else:
            now = time.time()
            query = "INSERT INTO bb (type, headline, body, creator,creation_time) VALUES (?, ?, ?, ?, ?)"
            qvals = ('topic',d[u'headline'],d[u'body'],d[u'user'],now)
            if h.db_do(query, qvals, db_path):
                message['success'] = True
            else:
                message['errors'].append(1003)
    return message

def list(target,d):
    message = h.msg()
    val = d[u'value'] * 10
    board_db = False
    if d[u'board']:
        if os.path.isfile('./bb/{}.sqlite'.format(d[u'board'])):
            board_db = './bb/{}.sqlite'.format(d[u'board'])

    if target == 'board':
        db_conn = sqlite3.connect(sys_db)
        c = db_conn.cursor()
        query = "SELECT * FROM boards ORDER BY name ASC LIMIT 10 OFFSET 0"
        rows = h.db_do(query, '', sys_db, False)
        for x in rows:
            row = {'headline': x[0],'body': x[3],'id': 0}
            message['rows'].append(row)
        if len(rows):
            message['success'] = True
        else:
            message['errors'].append(1007)
    elif d[u'board'] and board_db:
        if target == 'topic':
            query = 'SELECT rowid, headline, body, creator, creation_time FROM bb WHERE type = ? ORDER BY rowid ASC'
            qvals = ('topic',)
        elif target == 'post':
            if d[u'topic']:
                query = 'SELECT rowid, headline, body, creator, creation_time FROM bb WHERE type = ? and parent_id = ? ORDER BY creation_time DESC'
                qvals = ('post', d[u'topic'])
            else:
                query = False
                qvals = False
                message['errors'].append(1005)

        if query and qvals:
            rows = h.db_do(query, qvals, board_db, False)
            for x in rows:
                row = {'id': x[0], 'headline': x[1], 'body': x[2], 'creator': x[3], 'time': x[4]}
                message['rows'].append(row)
            if len(rows):
                message['success'] = True
            else:
                message['errors'].append(1007)
    else:
        message['errors'].append(1001)

    return message


