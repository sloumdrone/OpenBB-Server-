import os.path
import sqlite3

#-#-#-#-#-#
# query: string
# var: tuple of variables to insert into query
# db: string to db location
# singleton: if True, returns rowcount rather than returning rows
#-#-#-#-#-#
def db_do(query,var,db,singleton=True):
    if os.path.isfile(db):
        db_conn = sqlite3.connect(db)
        c = db_conn.cursor()
        c.execute(query,var)
        if singleton:
            output = c.rowcount
        else:
            output = []
            for x in c:
                output.append(x)
        db_conn.commit()
        db_conn.close()
        return output
    else:
        print 'ERROR: invalid path called for db_do: "{}"'.format(db)
        return False

#-#-#-#-#-#
# Returns a message skeleton
#-#-#-#-#-#
def msg():
    data = {
        'username': None,
        'success': False,
        'token': None,
        'body': None,
        'headline': None,
        'errors': [],
        'rows': []
    }

    return data
