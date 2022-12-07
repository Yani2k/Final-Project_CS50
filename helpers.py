from functools import wraps
from flask import g, request, redirect, url_for, render_template, session


def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if session.get("user_id") is None:
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
def rating(ratingW, ratingL, K):
  # probability the winner had to win
  PW = probability(ratingW, ratingL)
  # probability the loser had to lose
  PL = probability(ratingL, ratingW)
  
  ratingW += K * (1 - PW)
  ratingL += K * (0 - PL)

  new_elo = {}
  
  new_elo["EloP1"] = ratingW
  new_elo["ELoP2"] = ratingL
  
  return new_elo


def give_room(game_type, db):
  last_active_game = db.execute("SELECT * FROM games WHERE game_type = ? ORDER BY ID DESC LIMIT 1", game_type)
  last_room = last_active_game[0]["game_id"];
  if session.get("user_id") is None:
    # Check if unlogged players are trying to play ranked somewhere 
    if not last_active_game[0]["player2_id"]:
      db.execute("UPDATE games SET player2_id = -1, player2_elo = 800 WHERE game_id = ?", last_room)
      return last_room
    else:
      db.execute("INSERT INTO games (player1_id, player1_elo, game_type) VALUES (-1, 800, game_type)")
      return last_room + 1
  else:
    elo = db.execute("SELECT * FROM user WHERE id = ?", session["user_id"]) 
    if not last_active_game[0]["player2_id"]:
      db.execute("UPDATE games SET player2_id = ?, player2_elo = ? WHERE game_id = ?", session["user_id"], elo[0]["elo"], last_room) 
      return last_room          
    else:
      db.execute("INSERT INTO games (player1_id, player1_elo, game_type) VALUES (?, ?, ?)", session["user_id"], elo[0]["elo"], game_type)
      return last_room + 1