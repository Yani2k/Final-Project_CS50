#### Project title: Bulls&Cows
#### Video Demo:   https://www.youtube.com/watch?v=jm_8Kry1QBY&ab_channel=YaniEnchev
#### Description:
  This is my final project for the CS50 course. It's a web game implementation of the game Bulls and Cows, built on the Flask framework. 
  In the game players secretly choose 4 digit numbers and take turns trying to guess their opponent's number. After each guess the player gets information about how close his guess was. This information is in the form on 'Bulls' and 'Cows'. Every 'Cow' gotten means the player has guessed one number correctly, but has put it on the wrong position, while for every 'Bull' the number is also on the correct spot. The game is played until a player has guessed their opponents number, or has gotten 4 'Bulls' which is the same thing in this case.
  While the web page is implemented on Flask, the connection between the server and the different clients in the games is facilitated with flask-socketio. Flask socketio is needed because multiple players means players need to be informed immediately when another makes a decision, which is hard to implement with just Flask.
  For the reset password feature, the encryption token used to create the reset password link is created with a json web token.
  And for the front-end I've implemented most of it from the Bootstrap framework.
