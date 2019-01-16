from flask import flash
import sqlite3

from passlib.hash import md5_crypt

DB_FILE = "app.db"

# create table called users
def create_table():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("CREATE TABLE if not exists users (name TEXT, email TEXT, password TEXT, security_question TEXT, security_answer TEXT)")
    c.execute("CREATE TABLE if not exists events (name TEXT, user TEXT, date TEXT, location TEXT, description TEXT, tags TEXT, people TEXT, id INTEGER PRIMARY KEY AUTOINCREMENT)")
    # whose is to indicate whose contact this is, since all contacts for all users are stored in same table
    c.execute("CREATE TABLE if not exists contacts (whose TEXT, first TEXT, last TEXT, email TEXT, birthday TEXT, address TEXT)")
    db.commit()
    db.close()

# populate tables with example data
def populate_tables():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
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

# check if username and password combination is valid
def validate_user(email, password):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    users = c.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchall()
    if len(users) == 0 or not md5_crypt.verify(password, users[0][2]):
        flash("Username or password incorrect")
        db.close()
        return False
    db.close()
    return True

# returns the user with the given email, None if no user exists
def get_user_by_email(email):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    users = c.fetchall()
    user = None if len(users) == 0 else users[0]
    db.close()
    return user

# add user to database
def add_user(name, email, password, security_question, security_answer):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    password = md5_crypt.hash(password)
    params = (name, email, password, security_question, security_answer)
    c.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?)", params)
    db.commit()
    db.close()

# get events for certain username
def get_events_by_user(email):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    data = c.execute("SELECT * FROM events WHERE user = ? ORDER BY datetime(date) ASC", (email,)).fetchall()
    db.close()
    return data

def clear_old_events(email):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("DELETE FROM events WHERE date < datetime('now')")
    db.commit()
    db.close()

# add event
def add_event(user, name, desc, date, location, tags, people):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    params = (name, user, date, location, desc, tags, people)
    c.execute("INSERT INTO events (name, user, date, location, description, tags, people) VALUES(?, ?, ?, ?, ?, ?, ?)", params)
    db.commit()
    db.close()

def get_contacts_by_prefix(email, search):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    users = c.execute("SELECT * FROM contacts WHERE whose = ?", (email,)).fetchall()
    results = []
    for user in users:
        if search.lower() == user[1][0:len(search)].lower() or search.lower() == user[2][0:len(search)].lower() or search.lower() == user[3][0:len(search)].lower():
            results.append({"first": user[1], "last": user[2], "email": user[3], "bday": user[4], "address": user[5]})
    db.close()
    return results

# add a contact
def add_contact(user, first, last, email, bday, address):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    params = (user, first, last, email, bday, address)
    c.execute("INSERT INTO contacts VALUES(?, ?, ?, ?, ?, ?)", params)
    db.commit()
    db.close()

# get contacts by user
def get_contacts_by_user(email):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    users = c.execute("SELECT * FROM contacts WHERE whose = ?", (email,)).fetchall()
    retL = []
    for i in users:
        retL.append({"first": i[1], "last": i[2], "email": i[3], "bday": i[4], "address": i[5]})
    #print(retL)
    return retL
    db.commit()
    db.close()

def remove_from_pending(user, event_id):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    people_list = c.execute("SELECT people FROM events WHERE id = ?", (event_id,)).fetchone()[0].split(",")
    print(people_list)
    people_list.remove(user)
    people_list = ",".join(people_list)
    c.execute("UPDATE events SET people = ? WHERE id = ?", (people_list, event_id,))
    db.commit()
    db.close()

def get_pending_events(user):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    event_list = c.execute("SELECT * FROM events ORDER BY datetime(date) ASC").fetchall()
    results = []
    for event in event_list:
        people = event[6].split(",")
        for u in people:
            if user == u.strip():
                results.append(event)
    db.close()
    return results

def clone_event(user, event_id):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    event = c.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    new_event = (event[0], user, event[2], event[3], event[4], event[5], event[6])
    c.execute("INSERT INTO events (name, user, date, location, description, tags, people) VALUES(?, ?, ?, ?, ?, ?, ?)", new_event)
    db.commit()
    db.close()

def delete_event_db(user, event_id):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    if c.execute("SELECT user FROM events WHERE id = ?", (event_id,)).fetchone()[0] == user:
        c.execute("DELETE from events WHERE id = ?", (event_id,))
    db.commit()
    db.close()
