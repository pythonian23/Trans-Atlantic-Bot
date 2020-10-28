import flask
from flask import Flask
from threading import Thread


app = Flask("Trans-Atlantic-Bot")


@app.route("/")
def mainpage():
    return open("docs/index.html").read().replace("{{css}}", open("docs/main.css").read())

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run); server.start()
