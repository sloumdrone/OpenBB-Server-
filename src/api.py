import os.path, sqlite3, time, re
import auth

sys_db = './bb/sys.sqlite'

def add(target,d):
    val = d[u'value']
    db_path = './bb/{}.sqlite'.format(d[u'board'])
    if target == 'board':
        if re.match(r'^[\w-]{4,20}$',val):
            filepath = './bb/{}.sqlite'.format(val)
            if not os.path.isfile(filepath):
                db_conn = sqlite3.connect(filepath)
                c = db_conn.cursor()
                now = time.time()
                c.execute("CREATE TABLE bb (type text NOT NULL, headline text NOT NULL, body text NOT NULL,creator text NOT NULL, parent_id, creation_time integer NOT NULL)")
                db_conn.commit()
                db_conn.close()
                db_conn = sqlite3.connect(sys_db)
                c = db_conn.cursor()
                c.execute("INSERT INTO boards (name,creator,time,description) VALUES (?,?,?,?)",(val,d[u'user'],now,d[u'body']))
                db_conn.commit()
                db_conn.close()
                message = {'messages': ['Board created successfully!','New board name: {}'.format(val)], 'data': {'success': True}}
            else:
                message = {'messages': ['A board with the name "{}" already exists!'.format(val)], 'data': {'success': False}}
        else:
            message = {'messages': ['The board name "{}" is not allowed.'.format(val),'Boards must be letters, numbers, underscores, and hyphens only.','Boards names must be between 4 and 20 characters in length'],'data': {'success': False}}
    elif target == 'topic':
        if not re.match(r'^[-\w ]{1,50}$',d[u'headline']):
            message = {'messages': ['The topic name is not in the correct format','Please use between 1 and 50 letters, numbers, spaces, hyphens, and udnerlines'],'data': {'success': False}}
        elif not os.path.isfile(db_path):
            message = {'messages': ['The requested board does not exist','Run "list board" to verify the spelling','Then try again'],'data':{'success': False}}
        else:
            db_conn = sqlite3.connect('./bb/{}.sqlite'.format(d[u'board']))
            c = db_conn.cursor()
            now = time.time()
            c.execute("INSERT INTO bb (type, headline, body, creator,creation_time) VALUES (?, ?, ?, ?, ?)",('topic',d[u'headline'],d[u'body'],d[u'user'],now))
            db_conn.commit()
            db_conn.close()
            message = {'messages': ['Topic created successfully!','To verify, make sure your board is set','Then run "list topic"'],'data':{'success': True}}
    return message

def list(target,d):
    val = d[u'value'] * 10
    data_out = []
    if target == 'board':
        db_conn = sqlite3.connect(sys_db)
        c = db_conn.cursor()
        c.execute("SELECT * FROM boards ORDER BY name ASC LIMIT 10 OFFSET 0")
        for x in c:
            row = {'headline': x[0],'body': x[3],'id': 0}
            data_out.append(row)
    elif d[u'board'] and target in ['topic','post']:
        db_conn = sqlite3.connect(sys_db)
        c = db_conn.cursor()
        c.execute("SELECT * FROM boards WHERE name = ?",(d[u'board'],))
        success = c.fetchone()
        db_conn.close()
        if success:
            db_conn = sqlite3.connect('./bb/{}.sqlite'.format(d[u'board']))
            c = db_conn.cursor()
            if target == 'topic':
                c.execute('SELECT rowid, headline, body FROM bb WHERE type = ? ORDER BY rowid ASC',('topic',))
                for x in c:
                    row = {'id': x[0], 'headline': x[1], 'body': x[2]}
                    data_out.append(row)
            else:
                c.execute('SELECT * FROM bb WHERE type = ? and parent = ?')

    db_conn.commit()
    db_conn.close()
    message = {'messages': ['{} list compiled successfully'.format(target)],'data': {'success': True, 'rows': data_out}}
    return message


