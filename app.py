import os
from flask import Flask, render_template, session, request, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
# from datetime import datetime
from helpers import apology, login_required, rating, give_room
from flask_session import Session
from cs50 import SQL
from pyisemail import is_email
from flask_mail import Mail, Message
from decouple import config
from time import time
import jwt
from flask_socketio import SocketIO, send, emit, join_room

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)    

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#configuring mail settings
app.config["MAIL_DEFAULT_SENDER"] = config('MAIL_DEFAULT_SENDER')
app.config["MAIL_PASSWORD"] = config("MAIL_PASSWORD")
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = config("MAIL_USERNAME")

mail = Mail(app)

db = SQL("sqlite:///database.db")


# Configure the secret key for the encryption of the socket
app.config["SECRET_KEY"] = config("SECRET_KEY")
socketio = SocketIO(app)
socketio.run(app)
# socketio.init_app(app, cors_allowed_origins="*")

socketio.on("join_ranked")
def on_join_ranked():
  print("On join ranked")
  
socketio.on("join_friendly")
def on_join_friendly():
  print("On join friendly")
  
socketio.on("join_withfriend")
def on_join_withfriend():
  print("On join with friend")
  
socketio.on("join_bot")
def on_join_bot():
  print("On join bot")
      

# a helping function that's not in helpers cause it needs current session information
def get_reset_password_token(username, expires_in=600):
  return jwt.encode(
        {'reset_password': username, 'exp': time() + expires_in},
        config("SECRET_KEY"), algorithm='HS256')
        
def verify_reset_password_token(token):
  try:
    username = jwt.decode(token, config("SECRET_KEY"),
        algorithms=['HS256'])['reset_password']
  except:
    return False
  return True

def send_password_reset_email(username, email):
  token = get_reset_password_token(username)
  message = Message("Reset Password", recipients=[email])
  message.body = render_template("email/reset_password.txt", username=username, token=token)
  message.html = render_template("email/reset_password.html", username=username, token=token)
  mail.send(message)
  return redirect("/")
        

@app.route("/")
def home():
  return render_template("index.html")
 
@app.route("/login", methods=["GET", "POST"])
def login():  
  
  # Forget any user_id
  session.clear()

  if request.method == "POST":

    if not request.form.get("username_or_email"):
      return apology("must provide username", 400)

    elif not request.form.get("password"):
      return apology("must provide password", 400)

    rows = db.execute("SELECT * FROM user WHERE username = ?", request.form.get("username_or_email"))

    # if user hasn't tried to log in with their username, check emails
    if len(rows) != 1 :
      rows = db.execute("SELECT * FROM user WHERE email = ?", request.form.get("username_or_email"))
      if len(rows) != 1:
        return apology("Incorrect e-mail or username", 400)
    
    # by this point if we haven't returned then the row is on the correct thing and there is only one row
    if not check_password_hash(rows[0]["hash"], request.form.get("password")):
      return apology("invalid username and/or password", 400)    

    # Remember which user has logged in
    session["user_id"] = rows[0]["id"]
    session["user_username"] = rows[0]["username"]

    return redirect("/")

  if request.method == "GET":
    return render_template("login.html")
  

@app.route("/logout")
def logout():
  session.clear()
  return redirect("/")
  
  
@app.route("/register", methods=["GET", "POST"])
def register():  
  if request.method == "POST":
    
    starting_elo = 800
    
    username = request.form.get("username")
    if not username:
      return apology("must provide username", 400)

    password = request.form.get("password")
    if not password:
      return apology("must provide password", 400)
    
    if password != request.form.get("confirm"):
      return apology("passwords don't match", 400)
    
    email = request.form.get("email")
    
    #if an email-address has been provided
    if email:
      # check the validity of the email address
      if not is_email(email, check_dns=True):
        return apology("invalid email address", 400)

    row_username = db.execute("SELECT * FROM user WHERE username = ?", username)
    if len(row_username) == 1:
      return apology("Username is taken", 400)

    row_email = db.execute("SELECT * FROM user WHERE email = ?", email)
    if len(row_email) == 1:
      return apology("Email is taken", 400)
    
    db.execute("INSERT INTO user (username, hash, email, elo) VALUES (?, ?, ?, ?)", username, generate_password_hash(password), email, starting_elo)
    
    if email:
      message = Message("You are registered!", recipients=[email])
      message.body = "Congratulations, you have successfully registered to the bullsandcows website!"
      mail.send(message)
    
    return redirect("/")
    
  if request.method == "GET":
    return render_template("register.html")
  

@app.route("/forgotten-password", methods=["GET", "POST"])
def reset_password_request():
  if request.method == "GET":
    return render_template("reset_password_request_form.html")
  
  if request.method == "POST":
    email = request.form.get("email")
    
    if not email:
      return apology("You must input an email address", 400)
    
    row = db.execute("SELECT * FROM user WHERE email = ?", email)
  
    if len(row) == 0:
      return apology("Email address is not associated with any accounts", 400)

    return send_password_reset_email(row[0]["username"], email)


@app.route('/reset_password/<username>/<token>', methods=['GET', 'POST'])
def reset_password(username, token):
  
  # checking if someone is tempering with url parameters
  person = db.execute("SELECT * FROM user WHERE username = ?", username)
  if len(person) == 0:
    return apology("wrong url", 403)
  
  if request.method == "GET":
    verification_success = verify_reset_password_token(token)
    if not verification_success:
      return apology("invalid token", 400)
    return render_template("reset_password_form.html", username=username, token=token)
      
  if request.method == "POST":
    new_password = request.form.get("password")
    confirmation = request.form.get("confirm")
    
    if not new_password:
      return apology("You must input a password", 400)
    
    if new_password != confirmation:
      return apology("Passwords don't match", 400)
    
    db.execute("UPDATE user SET hash = (?) WHERE username = (?)", generate_password_hash(new_password), username)
    
    # if we're resetting the password through the email, then we surely have an email 
    # associated with the account
    message = Message("Reset Password", recipients=[person[0]["email"]])
    message.body = "Your password has been reset!"
    mail.send(message)
    
    return redirect(url_for('home'))


@app.route("/about")
def about():
    return render_template("about.html")
  
  
@app.route("/in_game/<type>")
def create_game(type):  
  # get id for the next game from games database
  game_id = 0
  return in_game(game_id, type)


def in_game(game_id, type):
  if type == 'pb':
    render_template("with_a_friend.html", game_id=game_id)
  elif type == 'friendly':
    render_template("friendly_ingame.html", game_id=game_id)
  elif type == 'ranked':
    render_template("ranked_ingame.html", game_id=game_id)
  return apology("something went wrong", 403)