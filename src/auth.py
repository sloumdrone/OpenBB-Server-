import hashlib, sqlite3,time
from secrets import PWSALT

sys_db = './bb/sys.sqlite'

def create_session_token(u):
    # generates a token based on time and username and a random seed
    # will return the token
    token = u + str(time.time())
    for x in range(100000):
        pwhash = hashlib.sha256()
        pwhash.update(token)
        token = pwhash.hexdigest()
    return token


def verify_password(u,p):
    provided = create_password_hash(p)
    db_conn = sqlite3.connect(sys_db)
    c = db_conn.cursor()
    c.execute("SELECT name FROM users WHERE name = ? and password = ?",(u,provided))
    success = c.fetchone()
    db_conn.commit()
    db_conn.close()
    if success:
        return True
    return False


def create_password_hash(p):
    val = p
    for x in range(100000):
        pwhash = hashlib.sha256()
        pwhash.update(val)
        val = pwhash.hexdigest()
    for x in range(100070):
        pshash = hashlib.sha512()
        pwhash.update(val + PWSALT)
        val = pwhash.hexdigest()
    return val
