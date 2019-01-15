from os import urandom
import urllib, json
from datetime import datetime

from flask import Flask, request, render_template, session, redirect, url_for, flash

from util.db_utils import validate_user, create_table, get_user_by_email, add_user, add_event, get_events_by_user, get_users_by_prefix

app = Flask(__name__)
app.secret_key = urandom(32)

MAPQUEST_KEY = "yRodQSl7GmyquNByYNcBBehTRM2F3Lgc"

@app.route("/", methods=["GET"])
def index():
    if "user" in session:
        events = get_events_by_user(session['user'])
        eventlist = [(event, get_location_image(event[3]), datetime.strptime(event[2], "%Y-%m-%d %H:%M:%S").strftime("%A, %B %d %Y at %I:%M%p") ) for event in events]
        print(events)
        return render_template("landing.html", user = session['user'], eventlist = eventlist )
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if validate_user(email, password):
            session["user"] = email
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    else:
        return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user" in session:
        return redirect(url_for("index"))
    if request.method == "GET":
        return render_template("signup.html")
    else:
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        security_question = request.form.get("security-question")
        security_answer = request.form.get("security-question")

        if not (name and email and password and confirm_password and security_question and security_answer):
            flash("All fields are required")
            return redirect(url_for("signup"))
        elif get_user_by_email(email) is not None:
            flash("That email address is already being used")
            return redirect(url_for("signup"))
        elif password != confirm_password:
            flash("Passwords did not match")
            return redirect(url_for("signup"))
        elif len(password) < 5:
            flash("Password must be 5 characters or longer")
            return redirect(url_for("signup"))
        elif '@' not in email or ' ' in email:
            flash("Please enter a valid email")
            return redirect(url_for("signup"))
        else:
            add_user(name, email, password, security_question, security_answer)
        return redirect(url_for("login"))

@app.route("/logout", methods=["GET"])
def logout():
    if "user" in session:
        session.pop("user")
    return redirect(url_for("login"))

@app.route("/create_event", methods=["GET", "POST"])
def create_event():
    if not "user" in session:
        return redirect(url_for("login"))
    if request.method == "GET":
        return render_template("create_event.html", user = session.get("user"))
    else:
        event_name = request.form.get("name")
        event_desc = request.form.get("description")
        event_date = request.form.get("date")
        event_time = request.form.get("time")
        event_location = request.form.get("location")
        event_tags = ""
        event_people = ""
        if not (event_name and event_desc and event_date):
            flash("Name, description, and date are mandatory")
            return redirect(url_for("create_event"))
        else:
            event_datetime = event_date + " - " + (event_time if event_time != " " else "12:00")
            try:
                event_datetime = datetime.strptime(event_datetime, "%m/%d/%Y - %H:%M")
            except:
                flash("There was an issue with the date/time entered")
                return redirect(url_for("create_event"))
            add_event(session["user"], event_name, event_desc, event_datetime, event_location, event_tags, event_people)
            return redirect(url_for("index"))

# def process_location(location):
#     req_url = "http://www.mapquestapi.com/geocoding/v1/address?outFormat=json&key=" + MAPQUEST_KEY + "&location=" + urllib.parse.urlencode({"location": location})
#     req = urllib.request.Request(req_url)
#     json_response = json.loads(urllib.request.urlopen(req).read())
#     lat = json_response["results"][0]["locations"]["latLng"]["lat"]
#     lon = json_response["results"][0]["locations"]["latLng"]["lon"]
#     return (lat, lon)

def get_location_image(location):
    req_url = "http://www.mapquestapi.com/geocoding/v1/address?outFormat=json&key=" + MAPQUEST_KEY + "&location=" + urllib.parse.urlencode({"location": location})
    req = urllib.request.Request(req_url)
    json_response = json.loads(urllib.request.urlopen(req).read())
    img_url = json_response["results"][0]["locations"][0]["mapUrl"]
    return img_url

@app.route("/user_suggestions")
def user_suggestions():
    search = request.args.get("search")
    results = get_users_by_prefix(search)
    json_response = json.dumps(results)
    return json_response


if __name__ == "__main__":
    create_table() # Only creates a table if it doesn't already exist
    app.debug = True;
    app.run()
