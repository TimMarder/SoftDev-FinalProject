from flask import Flask, request, render_template, session, redirect, url_for
from os import urandom
import db

app = Flask(__name__)
app.secret_key = urandom(32)

users = {"jaredasch":"pass"}

@app.route("/")
def index():
    try:
        db.create_table()
    except:
        pass
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if db.auth(username, password):
            return("welcome")
        else:
            return redirect("/")
    else:
        return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    return render_template("signup.html")

if __name__ == "__main__":
    app.debug = True;
    app.run()
