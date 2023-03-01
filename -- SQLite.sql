-- SQLite
CREATE TABLE user (id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT NOT NULL, hash TEXT NOT NULL, username TEXT NOT NULL, email VARCHAR(320),
elo FLOAT(6,2) NOT NULL);

.schema

SELECT * FROM user;
INSERT INTO user (id, username, elo, hash) VALUES (0, 'BOT', 800, '0');
INSERT INTO user (id, username, elo, hash) VALUES (-1, 'UNLOGGED', 800, '0');
UPDATE user SET elo = 800 WHERE id = 0;
UPDATE USER SET elo = 800 WHERE id = -1;
-- if the bot game or the game isn't finished, it doesnt't show up in the history
-- if that how i want it or should we think up a fix
-- yeah this will be a feature for now..
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


-- so it doesnt give any of the bot games because they lack some of the wanted fusions
-- I could easily make a placeholder profile for the bot and the
-- unlogged to solve this issue, idk if it's the most elegant
-- solution though
SELECT g.game_type AS type, g.time AS game_time, u1.username AS username1, u1.id AS id1, u1.elo AS elo1, u2.username AS username2, u2.id AS id2, u2.elo AS elo2, w.username AS winner_username, g.winner_id AS winners_id FROM games AS g INNER JOIN user AS u1 ON g.player1_id = u1.id INNER JOIN user AS u2 ON g.player2_id = u2.id INNER JOIN user AS w ON g.winner_id = w.id WHERE g.player1_id = 18 OR g.player2_id = 18;