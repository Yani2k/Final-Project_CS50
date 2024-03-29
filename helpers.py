from functools import wraps
from flask import g, request, redirect, url_for, render_template, session
from datetime import datetime

def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if session.get('user_id') is None:
      return redirect(url_for('login'))
    return f(*args, **kwargs)
  return decorated_function
  
  
def apology(message, code=400):
  """Render message as an apology to user."""
  def escape(s):
    """
    Escape special characters.
    https://github.com/jacebrowning/memegen#special-characters
        
    changing reserved characters using escape patterns
    """
    for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                    ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
      s = s.replace(old, new)
    return s
  return render_template("apology.html", top=code, bottom=escape(message)), code

# probability of the player with rating 1 to win
def probability(rating1, rating2):
  return 1.0 * 1.0 / (1 + 10 ** (1.0 * (rating2 - rating1) / 400))

# passing the ratings of the winner and the loser
# or to pass the game dictionary since it is mutable
def rating(ratingW, ratingL, K = 20):
  # probability the winner had to win
  PW = probability(ratingW, ratingL)
  # probability the loser had to lose
  PL = probability(ratingL, ratingW)
  
  ratingW += K * (1 - PW)
  ratingL += K * (0 - PL)

  new_elo = {}
  
  new_elo["EloW"] = round(ratingW, 2)
  new_elo["EloL"] = round(ratingL, 2)
  
  return new_elo

# used for ranked and for friendly games
# here we have a session['game_id'] definted for certain
def give_room(game_type, db):
  last_active_game = db.execute("SELECT * FROM games WHERE game_type = ? ORDER BY gameid_of_gametype DESC LIMIT 1", game_type)
  # tuka zaduljitelno imame user_id
  elo = db.execute("SELECT * FROM user WHERE id = ?", session["user_id"])
  last_room = 0
      
  # so that we have a way to start it up
  if len(last_active_game) != 0:
    last_room = last_active_game[0]["gameid_of_gametype"]
    socket_room = db.execute("SELECT * FROM socket_rooms WHERE room_id = ?", last_active_game[0]['game_id'])
    # on user disconnect we delete the socket
    # we can't delete the game on disconnect cause we want to delete only games not fired
    # but keep the finished games where the user disconnects after starting the game
    if len(socket_room) == 0:
      db.execute("DELETE FROM games WHERE game_id = ?", last_active_game[0]['game_id'])
      db.execute("INSERT INTO games (player1_id, player1_elo, game_type, gameid_of_gametype) VALUES (?, ?, ?, ?)", session["user_id"], elo[0]["elo"], game_type, last_room)
      return last_room
    
  if len(last_active_game) != 0 and not last_active_game[0]["player2_id"]:
    
    if(last_active_game[0]['player1_id'] == session['user_id']):
      return -1
      # a flag that something is wrong
    
    db.execute("UPDATE games SET player2_id = ?, player2_elo = ?, time = ? WHERE gameid_of_gametype = ? AND game_type = ?", session["user_id"], elo[0]["elo"], datetime.now(), last_room, game_type)     
  else:
    last_room += 1
    db.execute("INSERT INTO games (player1_id, player1_elo, game_type, gameid_of_gametype) VALUES (?, ?, ?, ?)", session["user_id"], elo[0]["elo"], game_type, last_room)
      
  return last_room
      
  
    
# returns a list of two numbers
# the first being the number of bulls
# the second the number of cows
def calculate_bulls_cows(guess, selected):
  bulls = sum(p == s for p, s in zip(guess, selected))
  cows = sum(p in selected for p in guess)
  return [bulls, cows - bulls]