from os import urandom
import urllib, json
from datetime import datetime

from flask import Flask, request, render_template, session, redirect, url_for, flash

from util.db_utils import *

app = Flask(__name__)
app.secret_key = urandom(32)

MAPQUEST_KEY = "yRodQSl7GmyquNByYNcBBehTRM2F3Lgc"
OPEN_WEATHER_MAP_KEY = "6bec20ccfcf2531d61bf02956f6049bb"

# login page
@app.route("/", methods=["GET"])
def index():
    if "user" in session:
        events = get_events_by_user(session.get("user"))
        clear_old_events(session.get("user"))
        eventlist = [generate_event_tuple(event) for event in events]
        pendinglist = [generate_event_tuple(event) for event in get_pending_events(session.get("user"))]
        return render_template("landing.html", user = session['user'], eventlist = eventlist, pendinglist = pendinglist )
    return redirect(url_for("login"))

# authenticate
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

# sign up
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

# logout
@app.route("/logout", methods=["GET"])
def logout():
    if "user" in session:
        session.pop("user")
    return redirect(url_for("login"))

# create event
@app.route("/create_event", methods=["GET", "POST"])
def create_event():
    if not "user" in session:
        return redirect(url_for("login"))
    if request.method == "GET":
        return render_template("create_event.html", user = session.get("user"))
    else:
        event_name = request.form.get("name")
        event_desc = request.form.get("description")

        event_day = request.form.get("day")
        event_month = request.form.get("month")
        event_year = request.form.get("year")
        event_hour = request.form.get("hour")
        event_minute = request.form.get("minute")

        event_location = request.form.get("location")
        event_tags = ""
        event_people = request.form.get("users")
        if not (event_name and event_desc and event_year and event_month and event_day and event_hour and event_minute):
            flash("Name, description, and date are mandatory")
            return redirect(url_for("create_event"))
        else:
            event_datetime = datetime(int(event_year), int(event_month), int(event_day), int(event_hour), int(event_minute))
            add_event(session["user"], event_name, event_desc, event_datetime, event_location, event_tags, event_people.strip())
            return redirect(url_for("index"))


def process_location(location):
    req_url = "http://www.mapquestapi.com/geocoding/v1/address?outFormat=json&key=" + MAPQUEST_KEY + "&location=" + urllib.parse.urlencode({"location": location})
    req = urllib.request.Request(req_url)
    json_response = json.loads(urllib.request.urlopen(req).read())
    lat = json_response["results"][0]["locations"][0]["latLng"]["lat"]
    lng = json_response["results"][0]["locations"][0]["latLng"]["lng"]
    return (lat, lng)

# get location image using API
def get_location_image(location):
    req_url = "http://www.mapquestapi.com/geocoding/v1/address?outFormat=json&key=" + MAPQUEST_KEY + "&location=" + urllib.parse.urlencode({"location": location})
    req = urllib.request.Request(req_url)
    json_response = json.loads(urllib.request.urlopen(req).read())
    img_url = json_response["results"][0]["locations"][0]["mapUrl"]
    return img_url

def get_location_weather(location, dt):
    date = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    lat, lng = process_location(location)
    req_url = "http://api.openweathermap.org/data/2.5/forecast?lat=" + str(lat) + "&lon=" + str(lng) + "&appid=" + OPEN_WEATHER_MAP_KEY
    req = urllib.request.Request(req_url)
    datapoints = json.loads(urllib.request.urlopen(req).read())["list"]
    for datapoint in datapoints:
        if(datapoint["dt"] > date.timestamp()):
            return "%02d&deg; F outside, %s" % (kelvin_to_farenheight(datapoint["main"]["temp"]), datapoint["weather"][0]["description"])
    return "Forecast not yet available"


# get user suggestions
@app.route("/user_suggestions")
def user_suggestions():
    if not "user" in session:
        return json.dumps({})
    search = request.args.get("search")
    results = get_contacts_by_prefix(session.get("user"), search)
    json_response = json.dumps(results)
    return json_response

# testing something out
@app.route("/testing")
def test():
    return render_template("test.html")


@app.route("/contacts")
def contacts():
    if not "user" in session:
        return redirect(url_for("login"))
    c = get_contacts_by_user(session.get("user"))
    return render_template("contacts.html", contact_list = c, user = session.get("user"))

# add contacts
@app.route("/add_contacts", methods = ["GET", "POST"])
def add_contacts():
    if not "user" in session:
        return redirect(url_for("login"))
    if request.method == "GET":
        return render_template("add_contact.html", user = session.get("user"))
    else:
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        bday = request.form.get("bday")
        address = request.form.get("address")
        print (session['user'], fname, lname, email, bday, address)
        add_contact(session['user'], fname, lname, email, bday, address)
        return (redirect("/contacts"))

@app.route("/decline_event/<int:event_id>")
def decline_event(event_id):
    if not "user" in session:
        return redirect(url_for("login"))
    remove_from_pending(session.get("user"), event_id)
    return redirect(request.referrer)

@app.route("/accept_event/<int:event_id>")
def accept_event(event_id):
    if not "user" in session:
        return redirect(url_for("login"))
    remove_from_pending(session.get("user"), event_id)
    clone_event(session.get("user"), event_id)
    return redirect(request.referrer)

@app.route("/delete_event/<int:event_id>")
def delete_event(event_id):
    if not "user" in session:
        return redirect(url_for("login"))
    delete_event_db(session.get("user"), event_id)
    return redirect(url_for("index"))

def generate_event_tuple(event):
    return (event, get_location_image(event[3]), datetime.strptime(event[2], "%Y-%m-%d %H:%M:%S").strftime("%A, %B %d %Y at %I:%M%p"), event[7], get_location_weather(event[3], event[2]) )

def kelvin_to_farenheight(k):
    return (k - 273.15) * 1.8 + 32

if __name__ == "__main__":
    create_table() # Only creates a table if it doesn't already exist
    app.debug = True;
    app.run()
