import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        self.connection.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, user_id TEXT UNIQUE, username TEXT, balance INTEGER DEFAULT 0, games_count INTEGER DEFAULT 0, date INTEGER, status INTEGER DEFAULT 0)')
        self.connection.execute('CREATE TABLE IF NOT EXISTS information (id INTEGER PRIMARY KEY, all_games_count INTEGER, withdraw_count INTEGER, users_count INTEGER, date INTEGER)')
        self.connection.execute('CREATE TABLE IF NOT EXISTS games (id INTEGER PRIMARY KEY, creator_id TEXT UNIQUE, creator_username TEXT, joiner_id INTEGER, joiner_username TEXT, bet_amount INTEGER, discription TEXT, status INTEGER DEFAULT 0)')
        self.connection.execute('CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, winer_1 TEXT DEFAULT Выбор, winer_2 TEXT DEFAULT Выбор, match_creator INTEGER)')
        self.connection.execute('CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY, comission INTEGER)')
        self.connection.execute('CREATE TABLE IF NOT EXISTS banned (id INTEGER PRIMARY KEY, user_id INTEGER)')


        self.connection.commit()

#----------ТАБЛИЦА users-----------------
    def add_user(self, user_id, username, date):
        with self.connection:
            return self.cursor.execute("INSERT INTO users (user_id, username, date) VALUES (?, ?, ?)",(user_id, username, date,),)
        
    def user_exists(self, user_id):
        with self.connection:
            result= self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return bool(len(result))
        
    def all_user_information(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall() 
        
    def get_user_balance(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id, )).fetchone()[0]
        
    def balance_minus_bet(self, bet, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (bet, user_id,))
        
    def balance_plus(self, bet, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (bet, user_id,))

    def update_user_games_count(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE users SET games_count = games_count + 1 WHERE user_id = ?", (user_id,))
        
    def all_users(self):
        with self.connection:
            return self.cursor.execute("SELECT user_id FROM users").fetchall()
        
    def update_status_arbitrage(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE users SET status=1 WHERE user_id=?", (user_id,))
        
    def update_status_free(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE users SET status=0 WHERE user_id=?", (user_id,))
        
    def get_user_status(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT status FROM users WHERE user_id=?", (user_id,)).fetchone()[0]

    

#---------ТАБЛИЦА information------------        
    def all_bot_information(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM information").fetchall()
        
    def update_user_count(self):
        with self.connection:
            return self.cursor.execute("UPDATE information SET users_count = users_count + 1")
        
    def update_games_count(self):
        with self.connection:
            return self.cursor.execute("UPDATE information SET all_games_count = all_games_count + 1")    

    def update_withdraws_count(self, amount):
        with self.connection:
            return self.cursor.execute("UPDATE information SET withdraw_count = withdraw_count + ?", (amount,))    
        


#----------ТАБЛИЦА games-----------       
    def game_exists(self, user_id):
        with self.connection:
            result= self.cursor.execute("SELECT * FROM games WHERE creator_id = ?", (user_id,)).fetchall()
            return bool(len(result))
        
    def add_game(self, creator_id, creator_username, bet_amount, discription):
        with self.connection:
            return self.cursor.execute("INSERT INTO games (creator_id, creator_username, bet_amount, discription) VALUES (?, ?, ?, ?)", (creator_id, creator_username, bet_amount, discription,))
        
    def get_game_information(self, creator_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM games WHERE creator_id = ?", (creator_id,)) 
             
    def delete_game(self, creator_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM games WHERE creator_id = ?",(creator_id,))
        
    def get_bet_amount(self, creator_id):
        with self.connection:
            return self.cursor.execute("SELECT bet_amount FROM games WHERE creator_id =? ",(creator_id,)).fetchone()[0] 

    def get_status(self, creator_id):
        with self.connection:
            return self.cursor.execute("SELECT status FROM games WHERE creator_id =? ",(creator_id,)).fetchone()[0]
        
    def get_all_active_games(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM games WHERE status = 0').fetchall()
        
    def activate_game(self, creator_id):
        with self.connection:
            return self.cursor.execute("UPDATE games SET status = 1 WHERE creator_id = ?", (creator_id,))
        
    def add_joiner(self, joiner_id, joiner_username, creator_id):
        with self.connection:
            return self.cursor.execute("UPDATE games SET joiner_id=?, joiner_username=? WHERE creator_id=?", (joiner_id, joiner_username, creator_id,))
        
    def get_joiner(self, creator_id):
        with self.connection:
            return self.cursor.execute("SELECT joiner_id FROM games WHERE creator_id = ?", (creator_id,)).fetchone()[0]
        
    def joiner_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM games WHERE joiner_id = ?", (user_id,)).fetchall()
            return bool(len(result))
        



#----------ТАБЛИЦА results----------- 
    def add_game_results(self, match_creator):
        with self.connection:
            return self.cursor.execute("INSERT INTO results (match_creator) VALUES (?)", (match_creator,))
        
    def add_winner_1(self, winner_1, match_creator):
        with self.connection:
            return self.cursor.execute("UPDATE results SET winer_1 = ? WHERE match_creator = ?", (winner_1, match_creator,))
        
    def add_winner_2(self, winner_2, match_creator):
        with self.connection:
            return self.cursor.execute("UPDATE results SET winer_2 = ? WHERE match_creator = ?", (winner_2, match_creator,))
        
    def get_results(self, match_creator):
        with self.connection:
            return self.cursor.execute("SELECT * FROM results WHERE match_creator = ?", (match_creator,)).fetchall()
        
    def delete_results(self, match_creator):
        with self.connection:
            return self.cursor.execute("DELETE FROM results WHERE match_creator = ?", (match_creator, ))



#----------ТАБЛИЦА admin-----------------
    def get_comission(self):
        with self.connection:
            return self.cursor.execute("SELECT comission FROM admin").fetchone()[0]



#----------ТАБЛИЦА banned-----------------
    def ban_user(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO banned (user_id) VALUES (?)", (user_id,))
        
    def unban_user(self, user_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM banned WHERE user_id = ?", (user_id,))
        
    def get_banned_users(self):
        with self.connection:
            return self.cursor.execute("SELECT user_id FROM banned").fetchall()