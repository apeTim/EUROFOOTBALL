from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from .MatchFunctionsFile import MatchFunctions
from .TicketFunctionsFile import TicketFunctions

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

class UserFunctions():
    def __init__(self):
        pass

    # Полезные методы
    def chatId(self, update):
        return update.message.chat_id
    
    # Обработка ошибок при вводе
    def notKeyboardShortcutError(self, update):
        self.bot.sendMessage(self.chatId(update), "Для взаимодействия с ботом используйте только клавиатуру!")
    
    def notDigitError(self, update):
        self.bot.sendMessage(self.chatId(update), "Вы прислали неверное число\n\nНеобходимо ввести только число без доп.символов и текста")
    
    # Функции Класса
    def choose_match_stage(self, update, context):
        context.user_data['action'] = 'Продать'
        markup = ReplyKeyboardMarkup([[x] for x in MATCH_DATA] + back_button, one_time_keyboard=False, resize_keyboard=True)
        self.bot.sendMessage(self.chatId(update), "Выберите стадию", reply_markup=markup)
        return 1

    def choose_match_date(self, update, context):
        if not update.message.text in MATCH_DATA:
            self.notKeyboardShortcutError(update)
            return 1

        context.user_data['match_stage'] = update.message.text
        markup = ReplyKeyboardMarkup(MATCH_DATA[update.message.text] + back_button, one_time_keyboard=False, resize_keyboard=True)
        if update.message.text == 'Груповой этап':
            self.bot.sendMessage(self.chatId(update), "Выберите группу", reply_markup=markup)
        else:
            self.bot.sendMessage(self.chatId(update), "Выберите дату", reply_markup=markup)
        return 2

    def choose_match_name(self, update, context):
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
        if not (update.message.text,) in context.user_data['active_matches_to_show']:
            self.notKeyboardShortcutError(update)
            return 3

        context.user_data['match_name'] = update.message.text
        markup = ReplyKeyboardMarkup(MATCH_TICKET_CLASSES + back_button, one_time_keyboard=False, resize_keyboard=True)
        self.bot.sendMessage(self.chatId(update), "Выберите категорию билета", reply_markup=markup)
        return 4

    def choose_match_tickets_number(self, update, context):
        if not (update.message.text in MATCH_TICKET_CLASSES[0] or update.message.text in MATCH_TICKET_CLASSES[1] or update.message.text in MATCH_TICKET_CLASSES[2]):
            self.notKeyboardShortcutError(update)
            return 4
        
        markup = ReplyKeyboardMarkup(back_button, one_time_keyboard=False, resize_keyboard=True)
        context.user_data['match_ticket_class'] = update.message.text
        self.bot.sendMessage(self.chatId(update), "Сколько билетов вы хотите продать? (Пришлите только число)", reply_markup=markup)
        return 5

    def stop(self, update, context):
        return ConversationHandler.END 