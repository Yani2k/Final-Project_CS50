-- SQLite
CREATE TABLE user (id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT NOT NULL, hash TEXT NOT NULL, username TEXT NOT NULL, email VARCHAR(320),
elo FLOAT(6,2) NOT NULL);

.schema

SELECT * FROM user;

-- DELETE FROM user;

CREATE TABLE games (game_id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT NOT NULL, player1_id INTEGER, player1_elo SMALLINT, player2_id INTEGER, player2_elo SMALLINT, winner_id INTEGER, time DATETIME);

-- Why am i having the elo also in the games table???
-- Probably shouldn't have it 

ALTER TABLE games ADD game_type TINYTEXT;

ALTER TABLE games ADD player1_num VARCHAR(5);

ALTER TABLE games ADD player2_num VARCHAR(5);

ALTER TABLE games ADD gameid_of_gametype INTEGER;

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

-- guesses is only for bot games
CREATE TABLE guesses(guess VARCHAR(5), guess_id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT NOT NULL, game_id INTEGER, user_number INTEGER);
ALTER TABLE guesses ADD bulls SMALLINT;
ALTER TABLE guesses ADD cows SMALLINT;

ALTER TABLE guesses ADD game_type TINYTEXT;
ALTER TABLE guesses DROP COLUMN game_type; -- not supported by spqlite

DROP TABLE guesses;

SELECT * FROM guesses;

-- how will i keep whos disconnected if i don't keep any identification
-- well i don't need that information as this information is only concerning the start of the game
-- if someone disconnects and then tries to reconnect that won't be supported while 
-- if someone wants to breach an ended game that will be cheched in other places
CREATE TABLE socket_rooms (room_id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT NOT NULL, player1 BOOL, player2 BOOL);

SELECT * FROM socket_rooms;

ALTER TABLE socket_rooms ADD player1_id INTEGER;
ALTER TABLE socket_rooms ADD player2_id INTEGER;

CREATE TABLE friends_list (id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT NOT NULL, list_owner_id INTEGER, friends_id INTEGER);

SELECT * FROM friends_list;