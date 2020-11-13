from flask import Flask
from threading import Thread


app = Flask("Trans-Atlantic-Bot")


@app.route("/")
def mainpage():
    return '<style>body{background:url("https://golangexample.com/content/images/2019/07/lazydockerv.gif")</style><h1 style="text-align: center;"><span style="text-decoration: underline;"><strong><span style="color: #ff0000; text-decoration: underline;">THE BOT IS VERY MUCH ALIVE THANK YOU</span></strong></span></h1>'

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run); server.start()
