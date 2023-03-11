#### Project title: Bulls&Cows
#### Video Demo:   https://www.youtube.com/watch?v=jm_8Kry1QBY&ab_channel=YaniEnchev
#### Description:
  This is my final project for the CS50 course. It's a web game implementation of 
  the game Bulls and Cows, built on the Flask framework.
  
  In the game players secretly choose 4 digit numbers and take turns trying to guess
  their opponent's number. After each guess the player gets information about how close
  their guess was. This information is in the form on 'Bulls' and 'Cows'. Every 'Cow' 
  gotten means the player has guessed one number correctly, but has put it on the wrong
  position, while for every 'Bull' the number is also on the correct spot. The game is 
  played until a player has guessed their opponents number, or has gotten 4 'Bulls'
  which is the same thing in this case.
  
  For the implementation in the regular games after each guess, the guess and the imformation
  that has come out from that guess will be displayed in the game history in the form of an
  ordered list.
  
  For the bot games and the algorithm with for the bot guesses, first all the possible guesses
  for the bot are stored in a database for the occasion. So that the calculation is done on the
  server side and doesn't strain the client's system, although that can be easily changed if
  desired. The algorithm for the guesses is constructed so that the guesses in the beginning are
  done quicker while the heavier calculations are done later on in the game. This is done because
  later on in the game the user also has more information and is therefore expected to take more 
  time making their guess.
  
  While the web page is implemented on Flask, the connection between the server and 
  the different clients in the games is facilitated with flask-socketio. Flask socketio
  is needed because multiple players means players need to be informed immediately when
  another makes a decision, which is hard to implement with just Flask.
  
  For the reset password feature, the encryption token used to create the reset password
  link is created with a json web token.
  
  For the front-end I've implemented most of it from the Bootstrap framework.
  
  For the bot game option. I'm saving the possible bot guesses in a database in the server
  as to keep most of the calculations 
