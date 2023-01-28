-- SQLite
CREATE TABLE user (id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT NOT NULL, hash TEXT NOT NULL, username TEXT NOT NULL, email VARCHAR(320),
elo FLOAT(6,2) NOT NULL);

.schema

SELECT * FROM user;

-- DELETE FROM user;

CREATE TABLE games (game_id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT NOT NULL, player1_id INTEGER, player1_elo SMALLINT, player2_id INTEGER, player2_elo SMALLINT, winner_id INTEGER, time DATETIME);

ALTER TABLE games ADD game_type TINYTEXT;

ALTER TABLE games ADD player1_num VARCHAR(5);

ALTER TABLE games ADD player2_num VARCHAR(5);

DROP TABLE bot_num_guesses;

CREATE TABLE bot_num_guesses (botgame_id INTEGER, remaining_possible_number VARCHAR(5), id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT NOT NULL);

SELECT * FROM games;

SELECT * FROM bot_num_guesses;

DELETE FROM bot_num_guesses;

DELETE FROM games;

DROP TABLE games;

CREATE TABLE initial_guesses (guess VARCHAR(5), id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT NOT NULL);
SELECT * FROM initial_guesses;

CREATE INDEX optimization_index ON bot_num_guesses(botgame_id, remaining_possible_number);

CREATE TABLE guesses(guess VARCHAR(5), guess_id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT NOT NULL, game_id INTEGER, user_number INTEGER);
ALTER TABLE guesses ADD bulls SMALLINT;
ALTER TABLE guesses ADD cows SMALLINT;