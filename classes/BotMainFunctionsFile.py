from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler

class BotMainFunctions:
    def __init__(self):
        self.main_keyboard = ReplyKeyboardMarkup([['Купить', 'Продать'], ['Мои объявления'], ['Мой профиль', 'Оценить пользователя'], ['Тех-поддержка']], one_time_keyboard=False, resize_keyboard=True)

    def any_text(self, update, context):
        update.message.reply_text("Для управления используй клавиатуру!", reply_markup=self.main_keyboard)

    def start_command(self, update, context):
        update.message.reply_text("Привет! Я создан, чтобы облегчить покупку/продажу билетов на Евро2020", reply_markup=self.main_keyboard)

    def stop_conversation(self, update, context):
        return ConversationHandler.END 