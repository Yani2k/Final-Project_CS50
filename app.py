import os
from flask import Flask, render_template, session, request, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
# from datetime import datetime
from helpers import apology, login_required, rating, give_room, calculate_bulls_cows
from flask_session import Session
from cs50 import SQL
from pyisemail import is_email
from flask_mail import Mail, Message
from decouple import config
from time import time
import jwt
from flask_socketio import SocketIO, send, emit, rooms, join_room, leave_room
from datetime import datetime
import pyperclip

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = config("SECRET_KEY")
Session(app)
socketio = SocketIO(app, manage_session=False)

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

# @socketio.on('my event')
# def on_event(data):
#   print("This time it works " + data['data'])

# socketio.init_app(app, cors_allowed_origins="*")

# то значи тук да правя всичко, тоест тук да влизам и в стаята
# в такъв случай няма смисъл от датабазата
# защото то няма както да се гледа, всъщност не е съвсем така
# защото датабазата е за да се засече кога е влязал втория човек, което още ще бъде нужно
@socketio.on("Get numbers of players")
def get_players():
  print(request.sid)
  print(session)
  full = False
  if 'game_type' not in session:
    session['game_type'] = 'with_friend'
  room = db.execute("SELECT * FROM games WHERE gameid_of_gametype = ? AND game_type = ?", session['game_id'], session['game_type'])
  join_room(room[0]['game_id'])
  socket_room = db.execute("SELECT * FROM socket_rooms WHERE room_id = ?", room[0]['game_id'])
  if len(socket_room) == 0:
    db.execute("INSERT INTO socket_rooms (player1, player1_id, room_id) VALUES (1, ?, ?)", session['user_id'], room[0]['game_id'])
  else:
    if socket_room[0]['player1_id'] == session['game_id']:
      # what things should be deleted here and whatnot
      # but we already delete shit before, here we'll happen to come only on the with friends games
      # Where there isn't anything else to delete
      return apology("Cannot play versus yourself!", 400)
    
    full = True
    db.execute("UPDATE socket_rooms SET player2 = 1, player2_id = ? WHERE room_id = ?", session['user_id'], room[0]['game_id'])
      
  print("Room is " + str(room[0]['game_id']))
  print(rooms(request.sid))
  if full == True:
    emit("game_start", broadcast=True, to=room[0]['game_id'])


# For when the user disconnects without finishing up the game
# So that we're not left with values in the session messing up with future games
# @socketio.on('disconnect')
# def on_disconnect():
#   # wast a test line    db.execute("SELECT * FROM games WHERE game_id = 1")
#   # these set off a shitton of errors in the disconnect, for some reason can't do db.execute in the disconnect
#   # room = db.execute("SELECT * FROM games WHERE gameid_of_gametype = ?", session['game_id'])
#   # to_clear = db.execute("SELECT * FROM socket_rooms WHERE room_id = ?", room[0]['game_id'])
#   # if len(to_clear) == 1:
#   #   db.execute("DELETE FROM socket_rooms WHERE room_id = ?", room[0]['game_id'])
  
#   # maybe i can try to do it a different way
  
#   if 'game_id' in session:
#     session.pop('game_id', None)
#   if 'game_type' in session:
#     session.pop('game_type', None)
    
@socketio.on("player disconnected 2")
def on_player_discon():
  print("player disconnected 2")
    
    
@socketio.on("player disconnected")
def on_player_disconnected():
  # maybe here it will work out ... # sometimes it does interestingly enough. Idk when why, why not
  print("on player disconnected")
  # room = db.execute("SELECT * FROM games WHERE gameid_of_gametype = ?", session['game_id']) here needs to be added also game_type if we ever come back to it
  # to_clear = db.execute("SELECT * FROM socket_rooms WHERE room_id = ?", room[0]['game_id'])
  # if len(to_clear) == 1:
  #   db.execute("DELETE FROM socket_rooms WHERE room_id = ?", room[0]['game_id'])
  #   leave_room(room[0]['game_id'])
  
  # if 'game_id' in session:
  #   session.pop('game_id', None)
  # if 'game_type' in session:
  #   session.pop('game_type', None)
    
@socketio.on('number_received')
def on_number_received(data):
  print("Inside number_received")
  num = data['number']
  first = data['first']
  
  # why is num an int at this point wtf?
  if (not str(num).isnumeric()) or len(str(num)) != 4:
    # if it's length is not 4 or it's not just numbers
    return apology("Something went wrong", 400)
  
  # session['game_id'] should be a thing at this point
  if session['game_id'] is None or session['game_type'] is None:
    # Idk if i can even return this from a socket funtion
    # Well see when i go to trying to start up this monstrosity
    return apology("Something went wrong", 400)
  
  row = db.execute("SELECT * FROM games WHERE gameid_of_gametype = ? AND game_type = ?", session['game_id'], session['game_type'])
  if row is None:
    # similar questions as above
    return apology("Something went wrong", 400)

  if first == "First number":
    print("Setting user's number in the database")
    if session['game_type'] == 'bot':
      db.execute("UPDATE games SET player1_num = ? WHERE gameid_of_gametype = ? AND game_type = 'bot'", num, session['game_id'])
      
    else:     
      if row[0]['player1_id'] == session['user_id']:
        # if row[0]['player1_num'] is None: # this is a pretty needless check
        db.execute("UPDATE games SET player1_num = ? WHERE gameid_of_gametype = ? AND game_type = ?", num, session['game_id'], session['game_type'])
        # emit('start_first', to=request.sid)
      
      elif row[0]['player2_id'] == session['user_id']:
        # if row[0]['player2_num'] is None: # same as above no case where this is needed
        db.execute("UPDATE GAMES SET player2_num = ? WHERE gameid_of_gametype = ? AND game_type = ?", num, session['game_id'], session['game_type'])
        # emit('start_second', to=session['game_id'])
      
      print(rooms(request.sid))
      game = db.execute("SELECT * FROM games WHERE gameid_of_gametype = ? AND game_type = ?", session['game_id'], session['game_type'])
      if game[0]['player1_num'] and game[0]['player2_num']:
        print("we should be emitting the numbers selected event")
        socket_room = db.execute("SELECT * FROM games WHERE gameid_of_gametype = ? AND game_type = ?", session['game_id'], session['game_type'])
        emit("numbers selected", {'sid of the second': request.sid}, to=socket_room[0]['game_id'])
  else:
    # we already have the selection set
    if session['game_type'] == 'bot':
      # this is a bot game and we have a guess set
      # I will do all the bot games actions here, yes some of it will duplicate the code for the overall case
      # but i think it will be more readable being separated like this
      game_info = db.execute("SELECT * FROM games WHERE gameid_of_gametype = ? AND game_type = 'bot'", session['game_id'])
      
      result_user_guess = calculate_bulls_cows(num, game_info[0]['player2_num'])
      if result_user_guess[0] == 4:
        emit('guess_result_bot', {'game_over': 'True', 'user_won': 'True'}, to=request.sid)
        # clean the database after the game so it doesn't clog up
        db.execute("DELETE FROM bot_num_guesses WHERE botgame_id = ?", session['game_id'])
        db.execute("DELETE FROM guesses WHERE game_id = ?", session['game_id'])
        # record the winner_id
        if 'user_id' in session:
          db.execute("UPDATE games SET winner_id = ? WHERE gameid_of_gametype = ? AND game_type = 'bot'", session['user_id'], session['game_id'])
        db.execute("UPDATE games SET winner_id = -1 WHERE gameid_of_gametype = ? AND game_type = 'bot'", session['game_id'])

        session.pop('game_id', None)
        session.pop('game_type', None)
        return
      
      bot_guesses = db.execute("SELECT * FROM guesses WHERE game_id = ?", session['game_id'])
      
      if len(bot_guesses) == 0:        
        # first guess from the bot, so no previous guesses
        print("setting up the first guess from the bot")
        current_bot_guess = db.execute("SELECT * FROM bot_num_guesses WHERE botgame_id = ? ORDER BY RANDOM() LIMIT 1", session['game_id'])
        result_bot_guess = calculate_bulls_cows(game_info[0]['player1_num'], current_bot_guess[0]['remaining_possible_number'])
        db.execute("INSERT INTO guesses (guess, game_id, bulls, cows, user_number) VALUES (?, ?, ?, ?, 2)", current_bot_guess[0]['remaining_possible_number'], session['game_id'], result_bot_guess[0], result_bot_guess[1])
        if result_bot_guess[0] == 4:
          emit('guess_result_bot', {'game_over': True, 'user_won': False, 'number': current_bot_guess[0]['remaining_possible_number']}, to=request.sid)
          db.execute("UPDATE games SET winner_id = 0 WHERE gameid_of_gametype = ? AND game_type = 'bot'", session['game_id'])
          # cleaning up the data from the database that is unneeded for future game handling
          db.execute("DELETE FROM bot_num_guesses WHERE botgame_id = ?", session['game_id'])
          db.execute("DELETE FROM guesses WHERE game_id = ?", session['game_id'])
          
          session.pop('game_id', None)
          session.pop('game_type', None)
          return
        else:
          print("Finished setting up the first bot guess")
          emit('guess_result_bot', {'bot_guess': current_bot_guess[0]['remaining_possible_number'], 'bot_guess_bulls': result_bot_guess[0], 'bot_guess_cows': result_bot_guess[1], 'user_guess': num, 'user_guess_bulls': result_user_guess[0], 'user_guess_cows': result_user_guess[1]}, to=request.sid)
          return         
    
      
      else:
        remaining_guesses = db.execute("SELECT * FROM bot_num_guesses WHERE botgame_id = ?", session['game_id'])
        for guess in remaining_guesses:
          suits_prev_guesses = True
          # the guesses table is only for bot games
          prev_guesses = db.execute("SELECT * FROM guesses WHERE game_id = ? AND user_number = 2", session['game_id'])
          for prev in prev_guesses:  
            # checking if the guess fits all previous data gathered from previous guesses from the bot
            if calculate_bulls_cows(prev['guess'], guess['remaining_possible_number']) != [prev['bulls'], prev['cows']]:
              suits_prev_guesses = False
              break
          if suits_prev_guesses == False:
            db.execute("DELETE FROM bot_num_guesses WHERE botgame_id = ? AND remaining_possible_number = ?", session['game_id'], guess['remaining_possible_number'])
          else:
            # we find the first guess in the database that satisfies our gathered data - guess['remaining_possible_number']!
            # We take it and use it as the current guess, while keeping the data in the session for the next guesses
            result_bot_guess = calculate_bulls_cows(guess['remaining_possible_number'], game_info[0]['player1_num'])
            # of male, tuka sum sravnqval sus 4isloto na bota pogreshka... uau
            if result_bot_guess[0] == 4:
              emit('guess_result_bot', {'game_over': 'True', 'user_won': 'False', 'number': guess['remaining_possible_number']}, to=request.sid)
              db.execute("DELETE FROM bot_num_guesses WHERE botgame_id = ?", session['game_id'])
              db.execute("DELETE FROM guesses WHERE game_id = ?", session['game_id'])
              db.execute("UPDATE games SET winner_id = 0 WHERE gameid_of_gametype = ? AND game_type = 'bot'", session['game_id'])
              session.pop('game_id', None)
              session.pop('game_type', None)
              return
              
            db.execute("INSERT INTO guesses (guess, game_id, bulls, cows, user_number) VALUES (?, ?, ?, ?, 2)", guess['remaining_possible_number'], session['game_id'], result_bot_guess[0], result_bot_guess[1])
            print("Finished updating the bot results dictionary and selecting the current bot guess")
            emit('guess_result_bot', {'bot_guess': guess['remaining_possible_number'], 'bot_guess_bulls': result_bot_guess[0], 'bot_guess_cows': result_bot_guess[1], 'user_guess': num, 'user_guess_bulls': result_user_guess[0], 'user_guess_cows': result_user_guess[1]}, to=request.sid)
            return

      
    else:
      if row[0]['player1_id'] == session['user_id']:
        selected = row[0]['player2_num']
      elif row[0]['player2_id'] == session['user_id']:
        selected = row[0]['player1_num']
      
      result = calculate_bulls_cows(num, selected)
      room = db.execute("SELECT * FROM games WHERE gameid_of_gametype = ? AND game_type = ?", session['game_id'], session['game_type'])
      if result[0] == 4:
        # this gets cleared in the disconnect
        # session.pop('game_id', None)
        if session['game_type'] == 'ranked':
          game = db.execute("SELECT * FROM games WHERE gameid_of_gametype = ? AND game_type = ?", session['game_id'], session['game_type'])
          print("ranked game over")
          if game[0]['player1_id'] == session['user_id']:
            new_elo = rating(game[0]['player1_elo'], game[0]['player2_elo'])
            print('Updating the elo')
            db.execute("UPDATE games SET winner_id = ?, player1_elo = ?, player2_elo = ? WHERE game_type = ? AND gameid_of_gametype = ?", session['user_id'], new_elo['EloW'], new_elo['EloL'], session['game_type'], session['game_id'])
            db.execute("UPDATE user SET elo = ? WHERE id = ?", new_elo['EloW'], session['user_id'])
            db.execute("UPDATE user SET elo = ? WHERE id = ?", new_elo['EloL'], game[0]['player2_id'])
            emit('game_over', {'winner_sid': request.sid, 'elo_won': new_elo['EloW'] - game[0]['player1_elo'], 'elo_lost': game[0]['player2_elo'] - new_elo['EloL']}, to=room[0]['game_id'])
            
          elif game[0]['player2_id'] == session['user_id']:
            new_elo = rating(game[0]['player2_elo'], game[0]['player1_elo'])
            print("updating elo 2")
            db.execute("UPDATE games SET winner_id = ?, player1_elo = ?, player2_elo = ? WHERE game_type = ? AND gameid_of_gametype = ?", session['user_id'], new_elo['EloL'], new_elo['EloW'], session['game_type'], session['game_id'])
            db.execute("UPDATE user SET elo = ? WHERE id = ?", new_elo['EloW'], session['user_id'])
            db.execute("UPDATE user SET elo = ? WHERE id = ?", new_elo['EloL'], game[0]['player1_id'])
            emit('game_over', {'winner_sid': request.sid, 'elo_won': new_elo['EloW'] - game[0]['player2_elo'], 'elo_lost': game[0]['player1_elo'] - new_elo['EloL']}, to=room[0]['game_id'])
            
        else:
          db.execute("UPDATE games SET winner_id = ? WHERE game_type = ? AND gameid_of_gametype = ?", session['user_id'], session['game_type'], session['game_id'])
          emit('game_over', {'winner_sid': request.sid}, to=room[0]['game_id'])
          
        session.pop('game_id', None)
        session.pop('game_type', None)
      else:
        emit('guess_result', {'result_from_sid': request.sid, 'bulls': result[0], 'cows': result[1]}, to=room[0]['game_id'])
        

    
# perhaps all of these could be meshed into a one more complex function to avoid the repetitious nature of these functions
# but at this point i'm not going to do it, it seems complicated
@socketio.on('join_ranked')
def on_join_ranked():
  room = give_room('ranked', db)
  if room == -1:
    # the flag went off
    return apology("Cannot play ranked vs yourself", 400)
  session['game_id'] = room
  session['game_type'] = 'ranked'
  print("Setting session game_id in join_ranked")
  game_url = url_for('in_game', game_id=room, type='ranked')
  emit('game_link', {'url': game_url}, to=request.sid)
  # return redirect(game_url)
  
  
@socketio.on('join_friendly')
def on_join_friendly():
  print("On join friendly")
  room = give_room('friendly', db)
  if room == -1:
    return apology("Cannot play friendly vs yourself", 400)

  session['game_id'] = room
  session['game_type'] = 'friendly'
  print("Setting session game_id in join friendly")
  game_url = url_for('in_game', game_id=room, type='friendly')
  emit('game_link', {'url': game_url}, to=request.sid)
  # return redirect(game_url)
  
  
@socketio.on('join_with_friend')
def on_join_with_friend():
  print("On join with friend")
  last_active_game = db.execute("SELECT * FROM games WHERE game_type = 'with_friend' ORDER BY gameid_of_gametype DESC LIMIT 1")
  elo = db.execute("SELECT * FROM user WHERE id = ?", session["user_id"])
  room = 1
  if len(last_active_game) != 0:
    room = last_active_game[0]['gameid_of_gametype'] + 1
  
  db.execute("INSERT INTO games (player1_id, player1_elo, game_type, gameid_of_gametype) VALUES (?, ?, ?, ?)", session["user_id"], elo[0]["elo"], 'with_friend', room)
  
  # join_room(room)
  session['game_id'] = room
  session['game_type'] = 'with_friend'
  print("Setting session game_id in join with friend")
  game_url = url_for('in_game', game_id=room, type='with_friend', _external=True)
  # now it's the correct url, but it doesnt add it to clipboard still
  print(game_url)
  emit('game_link', {'url': game_url}, to=request.sid)
  pyperclip.copy(game_url)
  # return redirect(game_url)

  
  
@socketio.on('join_bot')
def on_join_bot():
  last_active_game = db.execute("SELECT * FROM games WHERE game_type = 'bot' ORDER BY gameid_of_gametype DESC LIMIT 1")
  room = 1
  if len(last_active_game) != 0:
    # so we don't get an error on the first game
    # it's an extra check on every game after that but i believe that's not a major fault
    room = last_active_game[0]['gameid_of_gametype'] + 1

  if 'user_id' in session:
    elo = db.execute("SELECT * FROM user WHERE id = ?", session["user_id"])
    db.execute("INSERT INTO games (player1_id, player1_elo, game_type, player2_id, player2_elo, gameid_of_gametype, time) VALUES (?, ?, ?, ?, ?, ?, ?)", session["user_id"], elo[0]["elo"], 'bot', 0, 800, room, datetime.now())
  else:
    db.execute("INSERT INTO games (player1_id, player1_elo, game_type, player2_id, player2_elo, gameid_of_gametype, time) VALUES (?, ?, ?, ?, ?, ?, ?)", -1, 800, 'bot', 0, 800, room, datetime.now())
  
  session['game_id'] = room
  session['game_type'] = 'bot'
  # join_room(room) - so this works.. but some of the others don't
  # no need to join a room in a bot game since there is only one person ingame. This could probably be done without websockets too actually. Hmm.
  # But is it worth it to separate them that much. Plus i've already started implementing it with websocket so that's that
  game_url = url_for('in_game', game_id=room, type='bot')
  emit('game_link', {'url': game_url}, to=request.sid)
  # return redirect(game_url)
      

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
  # creating the session for the unlogged
  session['create_session'] = True
  
  # # testing the html
  # return render_template('bot_ingame.html')
  # emit('guess_result_bot', {'bot_guess': current_bot_guess[0]['remaining_possible_number'], 'bot_guess_bulls': result_bot_guess[0], 'bot_guess_cows': result_bot_guess[1], 'user_guess_bulls': result_user_guess[0], 'user_guess_cows': result_user_guess[1]}, to=request.sid)
  
  return render_template("index.html")
 
@app.route("/login", methods=["GET", "POST"])
def login():  
  
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

    session['user_id'] = rows[0]['id']
    session['user_username'] = rows[0]['username']

    return redirect("/")

  if request.method == "GET":
    return render_template("login.html")
  

@app.route("/logout")
def logout():
  session.clear()
  return redirect("/")
  
  
@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
  if request.method == 'POST':
    add_or_remove = request.form.get('add_or_remove')
    if add_or_remove == 'add':
      if session['user_id'] == user_id:
        #there was some tempering with the html file and unvalid data has been submitted
        return apology("Invalid data submitted", 400)
      is_there = db.execute("SELECT * FROM friends_list WHERE list_owner_id = ? AND friends_id = ?", session['user_id'], user_id)
      if len(is_there) == 0:
        # such friendship is not already there
        db.execute("INSERT INTO friends_list (list_owner_id, friends_id) VALUES (?,?)", session['user_id'], user_id)
      # after the friendship has been added to the database the rest of the actions are the same as when the page has been accessed through GET
    
    elif add_or_remove == 'remove':
      db.execute("DELETE FROM friends_list WHERE list_owner_id = ? AND friends_id = ?", session['user_id'], user_id)
    
  user = db.execute("SELECT * FROM user WHERE id = ?", user_id)
  if len(user) == 0:
    return apology("There is no such user!", 403)
  
  # I can do it with an if but is that the best way?
  # I can't actually do it with an if, cause it's different for every game
  # What happens here to the other info if one of the data is unavailable? 
  data = db.execute("SELECT g.game_type AS type, g.time AS game_time, u1.username AS username1, u1.id AS id1, u1.elo AS elo1, u2.username AS username2, u2.id AS id2, u2.elo AS elo2, w.username AS winner_username, g.winner_id AS winners_id FROM games AS g INNER JOIN user AS u1 ON g.player1_id = u1.id INNER JOIN user AS u2 ON g.player2_id = u2.id INNER JOIN user AS w ON g.winner_id = w.id WHERE g.player1_id = ? OR g.player2_id = ?", user_id, user_id)
  # games = db.execute("SELECT * FROM games WHERE player1_id = ? OR player2_id = ?",user_id, user_id)
  elo = db.execute("SELECT * FROM user WHERE id = ?", user_id)
  friends = db.execute("SELECT * FROM friends_list WHERE list_owner_id = ? AND friends_id = ?", session['user_id'], user_id)
  return render_template('user_profile.html', data=data, elo=elo, user_id=user_id, friends=len(friends))
  # return render_template('user_profile.html', games=games, elo=elo)
 
  
@app.route('/friend_list', methods=['POST', 'GET'])
def friend_list():
  if request.method == 'POST':
    id_to_remove = request.form.get('friend_id_remove')
    db.execute("DELETE FROM friends_list WHERE list_owner_id = ? AND friends_id = ?", session['user_id'], id_to_remove)
  friends = db.execute("SELECT l.friends_id AS fid, u.elo AS felo, u.username AS fusername FROM friends_list AS l INNER JOIN user AS u ON l.friends_id = u.id WHERE l.list_owner_id = ?", session['user_id'])
  # here there should be some innerjoins too
  return render_template('friendlist.html', friends=friends)  


@app.route('/leaderboard')
def leaderboard():
  leaders = db.execute("SELECT id, elo, username FROM user ORDER BY elo DESC LIMIT 5")
  # maybe in the future also ordered by the number of games
  # and also show the number of games
  # that will be interesting to do a bit later, needs 2 joins again and then order by the sum of both somehow
  return render_template('leaderboard.html', leaders=leaders)

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
      
      row_email = db.execute("SELECT * FROM user WHERE email = ?", email)
      if len(row_email) == 1:
        return apology("Email is taken", 400)

    row_username = db.execute("SELECT * FROM user WHERE username = ?", username)
    if len(row_username) == 1:
      return apology("Username is taken", 400)
    
    
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
  
# we're taking the game_id here for the users who enter the game via a game link
# provided by their friend. Otherwise we have the game id stored in the session dictionary
# I could make a separate game link for those, verify it with jwt token and have the game ids for
# the other game types not displayed in the url but that seems unnecessary at this point
# also as such the links will be different for the one entering the game via the link
# and the one creating the link unless i validate the creator with a jwt as well
# which appears unnecessary
@app.route("/in_game/<type>/<game_id>")
def in_game(game_id, type):
  # i should see if someone put a valid url that's expired
  # for example for bot games that'd make things notwork very well
  # i may put a jwt verification for such cases
  
  game = db.execute("SELECT * FROM games WHERE gameid_of_gametype = ? AND game_type = ?", game_id, type)
  if not game: 
    # someone put invalid url for some reason
    return apology("Game currently unavailable", 403)
  
  if type == 'bot':
    if not('game_id' in session) or game_id != str(session['game_id']):
      return apology("game id wrong", 400)
    
    # getting the possible numbers in the database, for easier generation by copying
    
    # number = ""
    # for i in range(10):
    #   number += chr(ord('0') + i)
    #   for j in range (10):
    #     if i != j:
    #       number += chr(ord('0') + j)
    #       for k in range(10):
    #         if k != j and k != i:
    #           number += chr(ord('0') + k)
    #           for r in range(10):
    #             if r != k and r != j and r != i:
    #               number += chr(ord('0') + r)
    #               db.execute("INSERT INTO initial_guesses(guess) VALUES (?)", number)
    #               number = number[:-1]
    #           number = number[:-1]
    #       number = number[:-1]
    #   number = number[:-1]
                  
                  
    # copying the numbers for faster generation
    db.execute("INSERT INTO bot_num_guesses(botgame_id, remaining_possible_number) SELECT ?, guess FROM initial_guesses", session['game_id'])
                  
    bot_number = db.execute("SELECT * FROM bot_num_guesses WHERE botgame_id = ? ORDER BY RANDOM() LIMIT 1", game_id)
    db.execute("UPDATE games SET player2_num = ? WHERE gameid_of_gametype = ? AND game_type = ?", bot_number[0]['remaining_possible_number'], game_id, type)
    return render_template('bot_ingame.html') 
  
  if type == 'with_friend':
    print('with_friend')
    # if the game is full, only works for this type of game though
    # cause the other types of games have both players in the database
    # by this point
    if session.get('user_id'):
      if game[0]['player1_id'] == session.get('user_id'):
        return render_template('with_a_friend_ingame.html')
        
      elif game[0]['player2_id'] is None:
        # here the same player cannot enter as the second player
        elo = db.execute("SELECT * FROM user WHERE id = ?", session['user_id'])
        db.execute("UPDATE games SET player2_id = ?, player2_elo = ?, time = ? WHERE gameid_of_gametype = ? AND game_type = ?", session['user_id'], elo[0]['elo'], datetime.now(), game_id, type)
        session['game_id'] = game_id
        session['game_type'] = 'with_friend'
        return render_template('with_a_friend_ingame.html')

      else:
        return apology("Game is in progress or already finished", 400)
      
    else:
      # if one is not logged in they can only access this game as the second player
      if game[0]['player2_id'] is None:
        db.execute("UPDATE games SET player2_id = ?, player2_elo = ?, time = ? WHERE gameid_of_gametype = ? AND game_type = ?", -1, 800, datetime.now(), game_id, type)
        # give them a default user_id for later uses 
        session['user_id'] = -1
        # set the session game_id for later use
        session['game_id'] = game_id
        session['game_type'] = 'with_friend'
        
        return render_template('with_a_friend_ingame.html')
      else:
        return apology("Game is in progress or already finished", 400)
  
  else:
    # if the game type is neither bot game nor with_friend
    if game[0]['player1_id'] != session.get('user_id') and game[0]['player2_id'] != session.get('user_id'):
      return apology("Game is in progress or already finished", 400)

  if type == 'ranked':
    return render_template('ranked_ingame.html')
  elif type == 'friendly':
    # aa zatova tuka da join-vam stajata - za da ne vadq game_id-to dva puti
    return render_template('friendly_ingame.html')


if __name__ == "__main__":
  socketio.run(app)