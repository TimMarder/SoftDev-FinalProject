from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

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

@app.route("/")
def index():
    msg = Message(subject = "Hello",
                  sender = "eventcalendar.stuy@gmail.com",
                  recipients = ["mykolyk@stuycs.org"])
    msg.body = "This message was sent via our flask app! \n\n-Team FiveKnees"
    mail.send(msg)
    return "Sent"

if __name__ == "__main__":
    app.debug = True
    app.run()
