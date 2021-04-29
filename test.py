import sqlite3
from telegram import ReplyKeyboardMarkup, Bot

bot = Bot('1774407270:AAF3LU2rQt8b3VIRY9BKn7p0v0ZwdDWsGt8')

#перенос пользователей
with sqlite3.connect('C:/Users/theco/Downloads/ticket_bot (1).db') as db_connection:
    cursor = db_connection.cursor()
    command = f'''SELECT * FROM users'''
    r = cursor.execute(command).fetchall()
    with sqlite3.connect('bot.db') as db2_connection:
        cursor2 = db2_connection.cursor()
        command = f'''INSERT INTO users (user_id, user_nickname, user_firstname, user_lastname, rating, rating_numbers, rated_users) VALUES (?, ?, ?, ?, 0, 0, "{"{}"}")'''
        for user in r:
            try:
                chat = bot.getChat(user[0])
                cursor2.execute(command, (user[0], chat.username, chat.first_name, chat.last_name))
            except Exception:
                print("Chat not found")
    cursor.close()

#перенос объявлений
with sqlite3.connect('C:/Users/theco/Downloads/ticket_bot (1).db') as db_connection:
    cursor = db_connection.cursor()
    matches = cursor.execute('''SELECT * FROM matches''')
    new_dict = {}
    for m in matches:
        new_dict[str(m[0])] = (str(m[2]) + str(m[3]), m[4])
    command = f'''SELECT * FROM tickets'''
    r = cursor.execute(command).fetchall()
    with sqlite3.connect('bot.db') as db2_connection:
        cursor2 = db2_connection.cursor()
        command = f'''INSERT INTO tickets (user_id, user_nickname, match_stage, match_group_or_date, match_name, match_ticket_class, match_tickets_number, match_tickets_sell_type, match_ticket_price, match_ticket_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        for ticket in r:
            try:
                chat = bot.getChat(ticket[1])
                cursor2.execute(command, (ticket[1], chat.username, translate_stages[ticket[3]], new_dict[str(ticket[0])][0], new_dict[str(ticket[0])][1], ticket[6], ticket[7], 'По одиночке', ticket[9], ticket[10]))
            except Exception:
                print("Chat not found")
    cursor.close()