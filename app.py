from flask import Flask, request, render_template, session, redirect, url_for
from os import urandom
import db

app = Flask(__name__)
app.secret_key = urandom(32)

users = {"jaredasch":"pass"}

# db.add_user("clara", "mohri")


@app.route("/")
def index():
    try: 
        db.create_table()
    except:
        pass
    return render_template("login.html")

@app.route("/login", methods = ["GET", "POST"])
def login_auth():
    username = request.form.get("username")
    password = request.form.get("password")
    if db.auth(username, password):
        return("welcome")
    else:
        return redirect("/")
        #return ((db.auth(username, password)))

@app.route("/create_account")
def create_acc():
    return render_template("create_account.html")

if __name__ == "__main__":
    app.debug = True
    app.run()
