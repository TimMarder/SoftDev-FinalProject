from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'clara.mohri@gmail.com',
    MAIL_PASSWORD = '',
))


mail = Mail(app)

@app.route("/")
def index():
    msg = Message("Hello",
                  sender = "clara.mohri@gmail.com",
                  recipients = "cmohri@stuy.edu")
    msg.body = "Hello"
    mail.send(msg)

if __name__ == "__main__":
    app.debug = True
    app.run()
