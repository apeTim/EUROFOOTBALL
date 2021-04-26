from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from .MatchFunctionsFile import MatchFunctions
from .TicketFunctionsFile import TicketFunctions
from .BotMainFunctionsFile import BotMainFunctions
import sqlite3

QUESTIONS = ["Выберите стадию", "Выберите группу/дату", "Выберите матч", "Выберите категорию билета", "Сколько билетов вы хотите продать? (Пришлите только число)", "Укажите минимальное количество билетов к продаже (Пришлите только число)", "Укажите цену за один билет (Пришлите только число)", "В объявлении укажите информацию о предложении. Желательно указать:\n-бумажный или электронный билет;\n-готовность встретится лично;\n-готовность к торгу;\n-форма оплаты(нал/бн/крипта);" ]

MATCH_DATA = {
    'Групповой этап': [['A', 'B'], ['C', 'D'], ['E', 'F']],
    '1/8 финала': [['26.06.21'], ['27.06.21'], ['28.06.21']],
    '1/4 финала': [['02.07.21'], ['03.07.21']],
    '1/2 финала': [['06.07.21'], ['07.07.21']],
    'Финал': [['11.07.21']]
}

MATCH_GROUPS_OR_DATES = ['A', 'B', 'C', 'D', 'E', 'F', '26.06.21', '27.06.21', '28.06.21', '02.07.21', '03.07.21', '06.07.21', '07.07.21', '11.07.21'  ]

MATCH_TICKET_CLASSES = [['1', '2', '3'], ['1OV', '2OV', '3OV'], ['VIP']]

back_button = [['Назад']]

menu_button = [['В главное меню']]

tomenu_button = [['В главное меню']]

class UserFunctions():
    def __init__(self, bot=''):
        if bot:
            self.bot = bot
        self.tomenu_keyboard = ReplyKeyboardMarkup([['В главное меню']], one_time_keyboard=False, resize_keyboard=True)
        self.bot_functions = BotMainFunctions()
        self.main_keyboard = ReplyKeyboardMarkup([['Купить', 'Продать'], ['Мои объявления'], ['Мой профиль', 'Оценить пользователя'], ['Тех-поддержка']], one_time_keyboard=False, resize_keyboard=True)
        pass

    # Полезные методы
    def chatId(self, update):
        return update.message.chat_id
    
    # Обработка ошибок при вводе
    def notKeyboardShortcutError(self, update):
        self.bot.sendMessage(self.chatId(update), "Для взаимодействия с ботом используйте только клавиатуру!")
    
    def notDigitError(self, update):
        self.bot.sendMessage(self.chatId(update), "Вы прислали неверное число\n\nНеобходимо ввести только число без доп.символов и текста")
    
    # Функции рейтинга
    def user_profile(self, update, context):
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            command = f'''SELECT * FROM users WHERE user_id = ?'''
            r = cursor.execute(command, (update.message.chat_id,)).fetchone()
            if r[5] == 0:
                rating = 'не определён'
            else:
                rating = round(r[4] / r[5], 2)
            self.bot.sendMessage(self.chatId(update), f"{r[2]} {r[3]}\n\nРейтинг: {rating}", reply_markup=self.main_keyboard)
            cursor.close()
    
    def rate_user_nickname(self, update, context):
        self.bot.sendMessage(self.chatId(update), "Введите никнем пользователя, которого хотите оценить", reply_markup=self.tomenu_keyboard)
        return 1

    def rate_user_relationships(self, update, context):
        if update.message.text == 'В главное меню':
            self.bot.sendMessage(self.chatId(update), "Главное меню", reply_markup=self.main_keyboard)
            return ConversationHandler.END
        if not self.bot_functions.check_user_in_db_by_nickname(update.message.text):
            self.bot.sendMessage(self.chatId(update), "Такого пользователя нет в нашей системе")
        else:
            context.user_data["rating_nikcname"] = update.message.text
            markup = ReplyKeyboardMarkup([['Знаком лично'], ['Имел дело в интернете'], ['Знакомые имели дело']] + back_button, resize_keyboard=True)
            self.bot.sendMessage(self.chatId(update), "В каких отношениях вы с пользователем", reply_markup=markup)
            return 2
        
    def rate_user_rating(self, update, context):
        if update.message.text == 'Назад':
            self.bot.sendMessage(self.chatId(update), "Введите никнем пользователя, которого хотите оценить", reply_markup=self.tomenu_keyboard)
            return 1
        self.bot.sendMessage(self.chatId(update), "Оцените пользователя от -10 до +10", reply_markup=ReplyKeyboardMarkup(back_button, resize_keyboard=True))
        return 3
    
    def rate_user_end(self, update, context):
        if update.message.text == 'Назад':
            markup = ReplyKeyboardMarkup([['Знаком лично'], ['Имел дело в интернете'], ['Знакомые имели дело']] + back_button, resize_keyboard=True)
            self.bot.sendMessage(self.chatId(update), "В каких отношениях вы с пользователем", reply_markup=markup)
            return 2
        if not update.message.text.replace('+', '').replace('-', '').isdigit():
            self.bot.sendMessage(self.chatId(update), "Введите число с префиксом (либо +, либо -)")
            return 3
        if not (int(update.message.text.replace('+', '').replace('-', '')) <= 10 and int(update.message.text.replace('+', '').replace('-', '')) >= 0):
            self.bot.sendMessage(self.chatId(update), "Минимальная оценка - -10\nМаксимальная оценка - +10")
            return 3
        with sqlite3.connect('bot.db') as db_connection:
            cursor = db_connection.cursor()
            if update.message.text[0] == '+':
                command = f'''UPDATE users SET rating = rating + ?, rating_numbers = rating_numbers + 1 WHERE user_nickname = ?'''
            else:
                command = f'''UPDATE users SET rating = rating - ?, rating_numbers = rating_numbers + 1 WHERE user_nickname = ?'''
            cursor.execute(command, (update.message.text.replace('+', '').replace('-', ''), context.user_data["rating_nikcname"]))
            db_connection.commit()
            cursor.close()
        self.bot.sendMessage(self.chatId(update), "Спасибо за оценку!", reply_markup=self.main_keyboard)
        return ConversationHandler.END


    # Функции Продажи/Покупки
    def choose_match_stage(self, update, context):
        context.user_data['action'] = 'Продать'
        markup = ReplyKeyboardMarkup([[x] for x in MATCH_DATA] + tomenu_button, one_time_keyboard=False, resize_keyboard=True)
        self.bot.sendMessage(self.chatId(update), "Выберите стадию", reply_markup=markup)
        return 1

    def choose_match_date(self, update, context):
        if update.message.text == 'В главное меню':
            self.bot.sendMessage(self.chatId(update), "Главное меню", reply_markup=self.main_keyboard)
            return ConversationHandler.END
        if not update.message.text in MATCH_DATA:
            self.notKeyboardShortcutError(update)
            return 1

        context.user_data['match_stage'] = update.message.text
        markup = ReplyKeyboardMarkup(MATCH_DATA[update.message.text] + back_button, one_time_keyboard=False, resize_keyboard=True)
        if update.message.text == 'Групповой этап':
            self.bot.sendMessage(self.chatId(update), "Выберите группу", reply_markup=markup)
        else:
            self.bot.sendMessage(self.chatId(update), "Выберите дату", reply_markup=markup)
        return 2

    def choose_match_name(self, update, context):
        if update.message.text == 'Назад':
            markup = ReplyKeyboardMarkup([[x] for x in MATCH_DATA] + tomenu_button, one_time_keyboard=False, resize_keyboard=True)
            self.bot.sendMessage(self.chatId(update), "Выберите стадию", reply_markup=markup)
            return 1
    
        if not update.message.text in MATCH_GROUPS_OR_DATES:
            self.notKeyboardShortcutError(update)
            return 2

        context.user_data['match_group_or_date'] = update.message.text
        active_matches = self.match_functions.get_active(context.user_data)
        context.user_data['active_matches_to_show'] = active_matches
        markup = ReplyKeyboardMarkup([[x[0]] for x in active_matches] + back_button, one_time_keyboard=False, resize_keyboard=True)
        self.bot.sendMessage(self.chatId(update), "Выберите матч", reply_markup=markup)
        return 3
    
    def choose_match_ticket_class(self, update, context):
        if update.message.text == 'Назад':
            markup = ReplyKeyboardMarkup(MATCH_DATA[context.user_data["match_stage"]] + back_button, one_time_keyboard=False, resize_keyboard=True)
            if context.user_data["match_stage"] == 'Групповой этап':
                self.bot.sendMessage(self.chatId(update), "Выберите группу", reply_markup=markup)
            else:
                self.bot.sendMessage(self.chatId(update), "Выберите дату", reply_markup=markup)
            return 2

        if not (update.message.text,) in context.user_data['active_matches_to_show']:
            self.notKeyboardShortcutError(update)
            return 3

        context.user_data['match_name'] = update.message.text
        markup = ReplyKeyboardMarkup(MATCH_TICKET_CLASSES + back_button, one_time_keyboard=False, resize_keyboard=True)
        self.bot.sendMessage(self.chatId(update), "Выберите категорию билета", reply_markup=markup)
        return 4

    def choose_match_tickets_number(self, update, context):
        if update.message.text == 'Назад':
            markup = ReplyKeyboardMarkup([[x[0]] for x in         context.user_data['active_matches_to_show']] + back_button, one_time_keyboard=False, resize_keyboard=True)
            self.bot.sendMessage(self.chatId(update), "Выберите матч", reply_markup=markup)
            return 3
        if not (update.message.text in MATCH_TICKET_CLASSES[0] or update.message.text in MATCH_TICKET_CLASSES[1] or update.message.text in MATCH_TICKET_CLASSES[2]):
            self.notKeyboardShortcutError(update)
            return 4
        
        markup = ReplyKeyboardMarkup(back_button + menu_button, one_time_keyboard=False, resize_keyboard=True)
        context.user_data['match_ticket_class'] = update.message.text
        self.bot.sendMessage(self.chatId(update), "Сколько билетов вы хотите продать/купить? (Пришлите только число)", reply_markup=markup)
        return 5

    def stop_conversation(self, update, context):
        self.bot.sendMessage(self.chatId(update), "Главное меню", reply_markup=self.main_keyboard)
        return ConversationHandler.END

    def stop(self, update, context):
        return ConversationHandler.END 