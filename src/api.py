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
    elif target == 'post' or target == 'reply':
        if target == 'reply' and not d[u'post']:
            message['errors'].append(1005)
            return message
        if d[u'topic'] and d[u'board']:
            query1 = "SELECT * FROM bb WHERE type = 'topic' and rowid = ?"
            qvals1 = (d[u'topic'],)
            if h.db_do(query1, qvals1, db_path) and d[u'body']:
                headline = d[u'headline'] if d[u'headline'] else ''
                now = time.time()
                parent = d[u'topic'] if target == 'post' else d[u'post']
                print parent
                query2 = "INSERT INTO bb (type, headline, body, creator, parent_id, creation_time) VALUES (?, ?, ?, ?, ?, ?)"
                qvals2 = (target,headline,d[u'body'],d[u'user'],parent,now)
                if h.db_do(query2, qvals2, db_path):
                    message['success'] = True
                else:
                    message['errors'].append(1003)
            else:
                message['errors'].append(1004)
        else:
            message['errors'].append(1005)

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


def view(target, d):
    message = h.msg()
    board_db = False
    if d[u'board']:
        if os.path.isfile('./bb/{}.sqlite'.format(d[u'board'])):
            board_db = './bb/{}.sqlite'.format(d[u'board'])

    if target == 'topic' and board_db:
        value = d[u'value'] if d[u'value'] else d[u'topic']
        query = "SELECT rowid, headline, body, creator, creation_time FROM bb WHERE rowid = ? and type = 'topic'"
        qvals = (value,)
        rows = h.db_do(query, qvals, board_db, False)
        if len(rows):
            message['headline'] = rows[0][1]
            message['body'] = rows[0][2]
            message['creator'] = rows[0][3]
            message['time'] = rows[0][4]
            message['success'] = True
        else:
            message['errors'].append(1007)
    elif target == 'post' and board_db:
        value = d[u'value'] if d[u'value'] else d[u'post']
        p_query = "SELECT rowid, headline, body, creator, creation_time FROM bb WHERE rowid = ?"
        p_qvals = (value,)
        r_query = "SELECT headline, body, creator, creation_time FROM bb WHERE parent_id = ? ORDER BY creation_time ASC"
        r_qvals = (value,)
        p_rows = h.db_do(p_query, p_qvals, board_db, False)
        r_rows = h.db_do(r_query, p_qvals, board_db, False)
        if p_rows:
            message['headline'] = p_rows[0][1]
            message['body'] = p_rows[0][2]
            message['creator'] = p_rows[0][3]
            message['time'] = p_rows[0][4]
            message['success'] = True

            if r_rows:
                for x in r_rows:
                    row = {'headline': x[0], 'body': x[1], 'creator': x[2], 'time': x[3]}
                    message['rows'].append(row)
            else:
                message['rows'].append({'headline': '', 'body': 'No replies yet...', 'creator': '', 'time': ''})
        else:
            message['errors'].append(1007)
    else:
        message['errors'].append(1001)

    return message
