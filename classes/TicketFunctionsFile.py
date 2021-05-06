import sqlite3
import json

class TicketFunctions:
    def __init__(self):
        pass

    def create_ticket(self, data, user_id, user_fullname):
        with sqlite3.connect('bot.db') as db_connection:
            pass_data = (user_id, user_fullname, data["match_stage"], data["match_group_or_date"], data["match_name"], data["match_ticket_class"], data["match_tickets_number"], data["match_tickets_sell_type"], data["match_ticket_price"], data["match_ticket_description"] )
            cursor = db_connection.cursor()
            command = f'''INSERT INTO tickets (user_id, user_fullname, match_stage, match_group_or_date, match_name, match_ticket_class, match_tickets_number, match_tickets_sell_type, match_ticket_price, match_ticket_description, ticket_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "Актуальное")'''
            cursor.execute( command, pass_data )
            db_connection.commit()
            cursor.close()
        return 1
    
    def delete_ticket_by_id(self, ticket_id):
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            command = f'''DELETE FROM tickets WHERE ticket_id = ?'''
            cursor.execute( command, (ticket_id, ) )
            db_connection.commit()
            cursor.close()
        return 1
    
    def edit_ticket(self, ticket_id, edit_field, new_value):
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            command = f'''UPDATE tickets SET {edit_field} = ? WHERE ticket_id = ?'''
            cursor.execute( command, (new_value, ticket_id ) )
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
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            if int(context["match_tickets_number"]) % 2 != 0:
                command = f'''SELECT * FROM tickets WHERE match_name = ? AND match_ticket_class = ? AND match_tickets_number >= ? AND match_tickets_sell_type = "По одиночке"'''
            else:
                command = f'''SELECT * FROM tickets WHERE match_name = ? AND match_ticket_class = ? AND match_tickets_number >= ?'''
            needed_tickets = cursor.execute( command, (context["match_name"], context["match_ticket_class"], context["match_tickets_number"] ) ).fetchall()
            new_needed_tickets = []
            all_users = self.get_all_users()
            for ticket in needed_tickets:
                user_id = ticket[1]
                needed_user = all_users[user_id]
                if needed_user[5] == 0:
                    user_trust = 'не определён'
                else:
                    user_trust = round(needed_user[4] / needed_user[5], 2)
                user_verificated, users_who_trusted = [needed_user[9], json.loads(needed_user[6])]
                new_users_who_trusted = []
                for user in users_who_trusted:
                    current_user_data = all_users[int(user)]
                    if current_user_data[5] == 0:
                        current_user_trust = 0
                    else:
                        current_user_trust = round(current_user_data[4] / current_user_data[5], 2)
                    new_users_who_trusted.append((users_who_trusted[user], current_user_trust, current_user_data[2] + ' ' + current_user_data[3], user))
                if user_verificated == 'VERIFICATED':
                    user_verificated = 'Пройдена'
                else:
                    user_verificated = 'Не пройдена'
                ticket += (user_trust, user_verificated, sorted(new_users_who_trusted, key=lambda x: -x[1]))
                new_needed_tickets.append(ticket)
            cursor.close()
        return new_needed_tickets
    
    def get_all_users(self):
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            command = f'''SELECT * FROM users'''
            r = cursor.execute(command).fetchall()
            all_users = {}
            for user in r:
                all_users[int(user[0])] = user
            cursor.close()
            return all_users
    
    def get_users_trust_and_rating(self, user_id):
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            command = f'''SELECT trust, trust_numbers, rating FROM users WHERE user_id = ?'''
            r = cursor.execute(command, (user_id, )).fetchone()
            if r[1] == 0:
                trust = 'не определён'
            else:
                trust = round(r[0] / r[1], 2)
            cursor.close()
            return (trust, r[2], json.loads(r[6]))