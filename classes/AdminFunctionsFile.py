from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
import sqlite3

class AdminFunctions:
    def __init__(self, bot):
        self.bot = bot
        self.main_keyboard = ReplyKeyboardMarkup([['🛒Купить', '💰Продать'], ['📜Мои объявления'], ['👤Мой профиль', '🌟Оценить пользователя'], ['✉️Тех-поддержка']], one_time_keyboard=False, resize_keyboard=True)
    
    def chatId(self, update):
        return update.message.chat_id
    
    def action_verificate(self, user_id):
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            command = '''UPDATE users SET rating = rating + 50, verification_status = "VERIFICATED" WHERE user_id = ?'''
            cursor.execute(command, (user_id, ))
            db_connection.commit()
    
    def action_decline(self, user_id):
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            command = '''UPDATE users SET verification_status = "DECLINED" WHERE user_id = ?'''
            cursor.execute(command, (user_id, ))
            db_connection.commit()

    def verificate_users(self, update, context):
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            users_to_verificate = cursor.execute('''SELECT user_id, verification_link FROM users WHERE verification_status = "WAITING"''').fetchall()
            context.user_data["users_to_verificate"] = [list(x) for x in users_to_verificate]
            if len(users_to_verificate) == 0:
                self.bot.sendMessage(self.chatId(update), "В данный момент нет заявок на верификацию!", reply_markup=self.main_keyboard)
                return ConversationHandler.END
            user = users_to_verificate[0]
            if len(users_to_verificate) == 1:
                keyboard = [
                    [
                        InlineKeyboardButton("Подтвердить", callback_data="verificate:0"),
                        InlineKeyboardButton("Отклонить", callback_data="decline:0")
                    ],  
                    [InlineKeyboardButton('🏠В главное меню', callback_data="gohome")]
                ]
                markup = InlineKeyboardMarkup(keyboard)
            else:
                keyboard = [
                [
                    InlineKeyboardButton("➡️Вперёд", callback_data='forward:1'),
                ],
                [
                    InlineKeyboardButton("Подтвердить", callback_data="verificate:0"),
                    InlineKeyboardButton("Отклонить", callback_data="decline:0")
                ],
                [InlineKeyboardButton('🏠В главное меню', callback_data="gohome")]
                ]
                markup = InlineKeyboardMarkup(keyboard)
            r = self.bot.sendMessage(self.chatId(update), f'''Ссылка на фотографию: {user[1]}''', reply_markup=markup, parse_mode='HTML')
            context.user_data["current_message_id"] = r.message_id
            return 1
            cursor.close()
        
    def switcher_verificate_users(self, update, context):
        if update.callback_query.data == 'gohome':
            self.bot.editMessageReplyMarkup(update.callback_query.from_user.id, context.user_data["current_message_id"], reply_markup=None)
            self.bot.sendMessage(update.callback_query.from_user.id, "Главное меню", reply_markup=self.main_keyboard)
            return ConversationHandler.END
        action, vrf_ticket_id = update.callback_query.data.split(':')
        if action == 'verificate':
            self.action_verificate(context.user_data["users_to_verificate"][int(vrf_ticket_id)][0])
            self.bot.answerCallbackQuery(update.callback_query.id, text='Успешно подтверждён!')
            context.user_data["users_to_verificate"][int(vrf_ticket_id)][1] = '\nПодтверждён!'
            return 1
        if action == 'decline':
            self.action_decline(context.user_data["users_to_verificate"][int(vrf_ticket_id)][0])
            self.bot.answerCallbackQuery(update.callback_query.id, text='Успешно отклонён!')
            context.user_data["users_to_verificate"][int(vrf_ticket_id)][1] = '\nОтклонён!'
            return 1

        self.bot.deleteMessage(update.callback_query.from_user.id, update.callback_query.message.message_id)
        if action == 'forward':
            user = context.user_data["users_to_verificate"][int(vrf_ticket_id)]
            if int(vrf_ticket_id) + 1 == len(context.user_data["users_to_verificate"]):
                keyboard = [
                [
                    InlineKeyboardButton("⬅️Назад", callback_data=f'back:{int(vrf_ticket_id) - 1}'),
                ],
                [
                    InlineKeyboardButton("Подтвердить", callback_data=f"verificate:{int(vrf_ticket_id)}"),
                    InlineKeyboardButton("Отклонить", callback_data=f"decline:{int(vrf_ticket_id)}")
                ],
                [InlineKeyboardButton('🏠В главное меню', callback_data="gohome")]
                ]
            else:
                keyboard = [
                [
                    InlineKeyboardButton("⬅️Назад", callback_data=f'back:{int(vrf_ticket_id) - 1}'),
                    InlineKeyboardButton("➡️Вперёд", callback_data=f'forward:{int(vrf_ticket_id) + 1}'),
                ],
                [
                    InlineKeyboardButton("Подтвердить", callback_data=f"verificate:{int(vrf_ticket_id)}"),
                    InlineKeyboardButton("Отклонить", callback_data=f"decline:{int(vrf_ticket_id)}")
                ], 
                [InlineKeyboardButton('🏠В главное меню', callback_data="gohome")]
                ]
            markup = InlineKeyboardMarkup(keyboard)
            r = self.bot.sendMessage(update.callback_query.from_user.id, f'''Ссылка на фотографию: {user[1]}''', reply_markup=markup, parse_mode='HTML')
            context.user_data["current_message_id"] = r.message_id
        if action == 'back':
            user = context.user_data["users_to_verificate"][int(vrf_ticket_id)]
            if int(vrf_ticket_id) == 0:
                keyboard = [
                [
                    InlineKeyboardButton("➡️Вперёд", callback_data=f'forward:{int(vrf_ticket_id) + 1}'),
                ],
                [
                    InlineKeyboardButton("Подтвердить", callback_data=f"verificate:{int(vrf_ticket_id)}"),
                    InlineKeyboardButton("Отклонить", callback_data=f"decline:{int(vrf_ticket_id)}")
                ],
                [InlineKeyboardButton('🏠В главное меню', callback_data="gohome")]
                ]
            else:
                keyboard = [
                [
                    InlineKeyboardButton("⬅️Назад", callback_data=f'back:{int(vrf_ticket_id) - 1}'),
                    InlineKeyboardButton("➡️Вперёд", callback_data=f'forward:{int(vrf_ticket_id) + 1}'),
                ],
                [
                    InlineKeyboardButton("Подтвердить", callback_data=f"verificate:{int(vrf_ticket_id)}"),
                    InlineKeyboardButton("Отклонить", callback_data=f"decline:{int(vrf_ticket_id)}")
                ],
                [InlineKeyboardButton('🏠В главное меню', callback_data="gohome")]
                ]
            markup = InlineKeyboardMarkup(keyboard)
            r = self.bot.sendMessage(update.callback_query.from_user.id, f'''Ссылка на фотографию: {user[1]}''', reply_markup=markup, parse_mode='HTML')
            context.user_data["current_message_id"] = r.message_id
        return 1