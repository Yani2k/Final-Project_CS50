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