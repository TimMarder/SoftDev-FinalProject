from os import urandom
import urllib, json

from flask import Flask, request, render_template, session, redirect, url_for, flash

app = Flask(__name__)
#app.secret_key = urandom(32)

HOLIDAY_STUB = "https://www.calendarindex.com/api/v1/holidays?country=US&year=2019&api_key="
HOLIDAY_KEY = "4ee45cd4aaa1b5179955938e84952c270cfb8563"
HOLIDAY_URL = HOLIDAY_STUB + HOLIDAY_KEY

@app.route("/")
def main():
    req = urllib.request.Request(HOLIDAY_URL, headers =  {"User-agent": "curl/7.43.0"})
    data = json.loads(urllib.request.urlopen(req).read())
    print(data)
    return render_template("holiday.html", i = data['response']['holidays'])


if __name__ == "__main__":
    app.debug = True;
    app.run()
