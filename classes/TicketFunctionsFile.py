import sqlite3

class TicketFunctions:
    def __init__(self):
        pass

    def create_ticket(self, data, user_id, user_nickname):
        with sqlite3.connect('bot.db') as db_connection:
            pass_data = (user_id, user_nickname, data["match_stage"], data["match_group_or_date"], data["match_name"], data["match_ticket_class"], data["match_tickets_number"], data["match_tickets_sell_type"], data["match_ticket_price"], data["match_ticket_description"] )
            cursor = db_connection.cursor()
            command = f'''INSERT INTO tickets (user_id, user_nickname, match_stage, match_group_or_date, match_name, match_ticket_class, match_tickets_number, match_tickets_sell_type, match_ticket_price, match_ticket_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            cursor.execute( command, pass_data )
            db_connection.commit()
            cursor.close()
        return 1
    
    def user_listed_tickets(self, user_id):
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            command = f'''SELECT * FROM tickets WHERE user_id = ?'''
            user_listed_tickets = cursor.execute( command, (user_id, ) ).fetchall()
            cursor.close()
        return user_listed_tickets
    
    def user_needed_tickets(self, user_id, context):
        print(context)
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            if int(context["match_tickets_number"]) % 2 != 0:
                command = f'''SELECT * FROM tickets WHERE match_name = ? AND match_ticket_class = ? AND match_tickets_number >= ? AND match_tickets_sell_type = "По одиночке"'''
            else:
                command = f'''SELECT * FROM tickets WHERE match_name = ? AND match_ticket_class = ? AND match_tickets_number >= ?'''
            needed_tickets = cursor.execute( command, (context["match_name"], context["match_ticket_class"], context["match_tickets_number"] ) ).fetchall()
            new_needed_tickets = []
            for ticket in needed_tickets:
                user_id = ticket[1]
                user_rating = self.get_users_rating(user_id)
                ticket += (user_rating, )
                new_needed_tickets.append(ticket)
            cursor.close()
        return new_needed_tickets
    
    def get_users_rating(self, user_id):
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            command = f'''SELECT rating, rating_numbers FROM users WHERE user_id = ?'''
            r = cursor.execute(command, (user_id, )).fetchone()
            rating = round(r[0] / r[1], 2)
            cursor.close()
            return rating