from os import urandom
import urllib, json
from datetime import datetime
from flask_mail import Mail, Message

from flask import Flask, request, render_template, session, redirect, url_for, flash

from util.db_utils import *

app = Flask(__name__)
app.secret_key = urandom(32)

#MAPQUEST_KEY = "yRodQSl7GmyquNByYNcBBehTRM2F3Lgc"
#OPEN_WEATHER_MAP_KEY = "6bec20ccfcf2531d61bf02956f6049bb"
#HOLIDAY_KEY = "4ee45cd4aaa1b5179955938e84952c270cfb8563"

with open("data/keys.json", 'r') as f:
    api_dict = json.load(f)

MAPQUEST_KEY = api_dict["MAPQUEST_KEY"]
OPEN_WEATHER_MAP_KEY = api_dict["OPEN_WEATHER_MAP_KEY"]
HOLIDAY_KEY = api_dict["HOLIDAY_KEY"]
HOLIDAY_STUB = "https://www.calendarindex.com/api/v1/holidays?country=US&year=2019&api_key="
HOLIDAY_URL = HOLIDAY_STUB + HOLIDAY_KEY

#email configuration
app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'eventcalendar.stuy@gmail.com',
    MAIL_PASSWORD = 'Eventcalendar!1',
))

mail = Mail(app)

# login page
@app.route("/", methods=["GET"])
def index():
    if "user" in session:
        clear_old_events(session.get("user"))
        events = get_events_by_user(session.get("user"))
        eventlist = [generate_event_tuple(event) for event in events]
        pendinglist = [generate_event_tuple(event) for event in get_pending_events(session.get("user"))]
        return render_template("landing.html", user = session['user'], eventlist = eventlist, pendinglist = pendinglist)
    return redirect(url_for("login"))

# get holidays using CalendarIndex API
def get_holidays():
    req = urllib.request.Request(HOLIDAY_URL, headers = {"User-agent": "curl/7.43.0"})
    data = json.loads(urllib.request.urlopen(req).read())
    holidays = data['response']['holidays']
    return data['response']['holidays']

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
            if event_people:
                emails = event_people.strip(",").strip()
                emails = emails.split(",")
                msg = Message(subject = "You have been invited to: " + event_name,
                              sender = "eventcalendar.stuy@gmail.com",
                              reply_to = session.get("user"),
                              recipients = emails)
                message = session.get("user") +  " has invited you to their event on " + event_month + "/" + event_day + "/" + event_year + "."
                message += ("\nDescription: " + event_desc)
                message += ("\nLocation: " + event_location)
                message += "\nSign up for EventCalendar: https://github.com/VinnyLin72/SoftDev-FinalProject"

                
                msg.body = message
                mail.send(msg)
            event_datetime = datetime(int(event_year), int(event_month), int(event_day), int(event_hour), int(event_minute))
            add_event(session["user"], event_name, event_desc, event_datetime, event_location, event_tags, event_people.strip())
            return redirect(url_for("index"))


def process_location(location):
    if location == "":
        return (None, None)
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
    if lat == None and lng == None:
        return "Forecast not available"
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

        if (not fname) or (not lname):
            flash("First name and last name are required fields.")
            return redirect("/add_contacts")

        if bday:
            if len(bday) != 5 :
                flash ("Birthday not in correct format")
                return redirect("/add_contacts")
            if bday[2] != "/":
                flash ("Birthday not in correct format")
                return redirect("/add_contacts")
            try:
                if int(bday[:2]) > 12:
                    flash("Please enter a valid date")
                    return redirect("/add_contacts")
                if int(bday[3:]) > 31:
                    flash("Please enter a valid date")
                    return redirect("/add_contacts")
            except:
                flash("Please enter a valid date")
                return redirect("/add_contacts")


        add_contact(session['user'], fname, lname, email, bday, address)

        event_name = fname + " " + lname + "'s Birthday"
        event_desc = fname + " " + lname + "'s Birthday"
        bday = bday.split("/")
        event_datetime = "2019-" + "-".join(bday) +"  00:00:00"
        event_location = ""
        event_tags = ""
        event_people = ""
        add_event(session["user"], event_name, event_desc, event_datetime, event_location, event_tags, event_people)        
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

@app.route("/edit_event/<int:event_id>", methods=["GET", "POST"])
def edit_event(event_id):
    if not "user" in session:
        return redirect(url_for("login"))
    if request.method == "GET":
        event = get_event_by_id(event_id)
        event_datetime = datetime.strptime(event[2], "%Y-%m-%d %H:%M:%S")
        form = {"name": event[0], "location": event[3], "description": event[4], "people": event[6], "month": event_datetime.month, "day": event_datetime.day, "year": event_datetime.year, "hour": event_datetime.hour, "minute": event_datetime.minute}
        return render_template("edit_event.html", form=form, id=event_id)
    else:   # request.method == "POST"
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
            return redirect(request.referrer)
        else:
            event_datetime = datetime(int(event_year), int(event_month), int(event_day), int(event_hour), int(event_minute))
            update_event(session.get("user"), event_id, event_name, event_desc, event_datetime, event_location, event_tags, event_people.strip())

            # send an email to update those invited

            if event_people:
                emails = event_people.strip(",").strip()
                emails = emails.split(",")
                msg = Message(subject = "You have been invited to: " + event_name,
                              sender = "eventcalendar.stuy@gmail.com",
                              reply_to = session.get("user"),                                                                                                                                      
                              recipients = emails)
                message = session.get("user") +  " has invited you and updated their event on " + event_month + "/" + event_day + "/" + event_year + "."
                message += ("\nDescription: " + event_desc)
                message += ("\nLocation: " + event_location)
                message += "\nSign up for EventCalendar: https://github.com/VinnyLin72/SoftDev-FinalProject"
                msg.body = message
                mail.send(msg)
            
            return redirect(url_for("index"))

@app.route("/event_location_image/<int:event_id>")
def event_location_image(event_id):
    event = get_event_by_id(event_id)
    return get_location_image(event[3])

@app.route("/forecast/<int:event_id>")
def forecast(event_id):
    event = get_event_by_id(event_id)
    return get_location_weather(event[3], event[2])

# enter in email address
@app.route("/recover_password")
def recover_password():
    return render_template("change_password.html")

# if email exists, answer security question
@app.route("/security_ques", methods = ["GET", "POST"])
def security_ques():
    if request.method == "POST":
        e = request.form.get("email")
        a = get_securityques(e)
        if email_exists(e):
            session['email'] = e
            session['question'] = a[0][0]
            return render_template("securityq.html", email = request.form.get("email"), question = session['question'])
        else:
            flash("Email does not exist")
            return redirect("/recover_password")
    if request.method == "GET":
        return render_template("securityq.html", email = session['email'], question = session['question'])

# if security question is answererd correctly, allow user to reset password
@app.route("/answer", methods = ["GET", "POST"])
def reset():
    if request.method == "POST":
        answer = request.form.get("answer")
        check = get_securityans(session["email"])[0][0]
        if answer == check:        
            return render_template("reset_password.html", email = session["email"])
        flash("Incorrect answer")
        return redirect("/security_ques")
    if request.method == "GET":
        return render_template("reset_password.html", email = session["email"])
    
#check if answer match. If they do, redirect to login. If not, redirect to /answer
@app.route("/check_answers", methods = ["GET", "POST"])
def check_answers():
    if request.method == "POST":
        p1 = request.form.get("p1")
        p2 = request.form.get("p2")
        if not (p1 and p2):
            flash("All fields are required")
            return redirect("/answer")
        if p1 == p2:
            if len(p1) < 5:
                flash("Password must be 5 characters or longer")
                return redirect("/answer")
            resetpassword(session['email'], p1)
            flash("Your password has succesfully been reset!")
            return redirect("/")
        else:
            flash("Passwords do not match")
            return redirect("/answer")

# def generate_event_tuple(event):
#     return (event, get_location_image(event[3]), datetime.strptime(event[2], "%Y-%m-%d %H:%M:%S").strftime("%A, %B %d %Y at %I:%M%p"), event[7], get_location_weather(event[3], event[2]) )

def generate_event_tuple(event):
    date_str = datetime.strptime(event[2], "%Y-%m-%d %H:%M:%S").strftime("%A, %B %d, %Y at %I:%M%p")
    return {"id": event[7], "name": event[0], "desc": event[4], "date": date_str, "location": event[3]}

def kelvin_to_farenheight(k):
    return (k - 273.15) * 1.8 + 32

if __name__ == "__main__":
    try:
        create_table(get_holidays()) # Only creates a table if it doesn't already exist
    except:
        print("It appears there is an issue with your API keys. Please check that they are all in keys.json, and that they are all correct.")
    else:
        app.debug = True;
        app.run()
