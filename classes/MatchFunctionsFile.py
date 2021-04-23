import sqlite3

class MatchFunctions:
    def __init__(self):
        print('MatchFunctions connected')
    
    def get_active(self, user_context):
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            command = '''SELECT name FROM matches WHERE match_stage = ? AND match_group_or_date = ?'''
            active_matches = cursor.execute( command, ( user_context["match_stage"], user_context["match_group_or_date"] ) ).fetchall()
            print(active_matches)
            cursor.close()
        return active_matches