import sqlite3

DB_FILE = "app.db"

# create table called users
def create_table():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("CREATE TABLE users (user TEXT, password TEXT)")
    c.execute("CREATE TABLE events (name TEXT, user TEXT, date TEXT, location TEXT, description TEXT, tags TEXT, people TEXT)")
    #print('created table')

    hardcoded_vals = [('clara', 'm'), ('jared', 'a'), ('vincet', 'l')]
    for i in hardcoded_vals:
        c.execute("INSERT INTO users VALUES(?, ?)", i)
        print(i)
    params = ("topher", "m")
    c.execute("INSERT INTO users VALUES(?, ?)", params)

    val = ('birthday', 'clara', '02-18-2019', 'nyc', 'my birthday', 'birthday', 'none')
    c.execute("INSERT INTO events VALUES(?, ?, ?, ?, ?, ?, ?)", val)
    
    db.commit()
    db.close()

# check if username and password are in database
def auth(username, password):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    data = c.execute("SELECT * FROM users")
    #print("hello")
    for row in data:
        print("row: ", row)
        if row[0] == username and row[1] == password:
            db.close()
            return True
    db.close()
    return False

# check if username already exists
def check_user(username):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    data = c.execute ("SELECT * FROM users")
    for row in data:
        if row[0] == username:
            db.close()
            return True
    db.close()
    return False

# add user to database
def add_user(username, password):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    params = (username, password)
    c.execute("INSERT INTO users VALUES(?, ?)", params)
    db.commit()
    db.close()

# get events for certain username
def get_events(username):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    command = 'SELECT * FROM events where "user" = "' + username + '"'
    data = c.execute(command)
    retL = []
    for row in data:
        retL.append(row)    
    db.close()
    return retL
    
