from flask import Flask, request, redirect, render_template, session
import urllib.request
import sys
import os
from sqlalchemy import create_engine
from flask_session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://dej:dej@localhost:5432/callcentre")
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    try:
        user = session['username']
        return render_template("index.html")
    except KeyError:
        return render_template("login.html")

@app.route("/details")
def get_details():
    print("Okay")
    number = request.args['numero']
    print(number)
    operationGen = "GETGEN"

    #http://localhost:8080/CallCentre/Resource?OPERATION=GETIMSI
    urlIMSI = "http://localhost:8080/CallCentre/Resource?OPERATION=GETIMSI"
    resultImsi = urllib.request.urlopen(urlIMSI)
    imsi = resultImsi.read().decode("utf-8")
    urlGen =  "http://localhost:8080/CallCentre/Resource?OPERATION=GETGEN"
    resultGen = urllib.request.urlopen(urlGen)
    gen = resultGen.read().decode("utf-8")

    return render_template("display.html", imsi=imsi, gen=gen, number=number)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                    {"username": username, "password": generate_password_hash(password)})
        db.commit()
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        
        user = db.execute("SELECT * from users WHERE username=:username",
                    {"username": username}).fetchone()
        if user is None:
            return "User doesnt Exist"
        else:
            password = request.form.get("password")
            if not check_password_hash(user.password, password):
                return render_template("Incorrect Password")
            else:
                session['username'] = username
                return render_template("index.html")
            
            
@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")
