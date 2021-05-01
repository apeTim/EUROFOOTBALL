from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from .MatchFunctionsFile import MatchFunctions
from .TicketFunctionsFile import TicketFunctions
from .UserFunctionsFile import UserFunctions

back_button = [['⬅️Назад']]

MATCH_TICKET_CLASSES = [['1', '2', '3'], ['1OV', '2OV', '3OV'], ['VIP']]

class SellerFunctions(UserFunctions):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.match_functions = MatchFunctions()
        self.ticket_functions = TicketFunctions()

    # Функции Класса
    def match_tickets_sell_type(self, update, context):
        if update.message.text == '⬅️Назад':
            markup = ReplyKeyboardMarkup(MATCH_TICKET_CLASSES + back_button, one_time_keyboard=False, resize_keyboard=True)
            self.bot.sendMessage(self.chatId(update), "Выберите категорию билета", reply_markup=markup)
            return 4
        if (not update.message.text.isdigit()) or (not int(update.message.text) > 0):
            self.notDigitError(update)
            return 5

        markup = ReplyKeyboardMarkup([['По одиночке'], ['По парам']] + back_button, one_time_keyboard=False, resize_keyboard=True)
        context.user_data['match_tickets_number'] = update.message.text
        self.bot.sendMessage(self.chatId(update), "Как вы хотите продавать билеты?", reply_markup=markup)
        return 6
        
    def match_ticket_price(self, update, context):
        if update.message.text == '⬅️Назад':
            markup = ReplyKeyboardMarkup(back_button, one_time_keyboard=False, resize_keyboard=True)
            self.bot.sendMessage(self.chatId(update), "Сколько билетов вы хотите продать? (Пришлите только число)", reply_markup=markup)
            return 5
        if not update.message.text in ['По одиночке', 'По парам']:
            self.notKeyboardShortcutError(update)
            return 6

        markup = ReplyKeyboardMarkup(back_button, one_time_keyboard=False, resize_keyboard=True)
        context.user_data['match_tickets_sell_type'] = update.message.text
        self.bot.sendMessage(self.chatId(update), "Укажите цену за один билет (Пришлите только число)", reply_markup=markup)
        return 7
    
    def match_ticket_description(self, update, context):
        if update.message.text == '⬅️Назад':
            markup = ReplyKeyboardMarkup([['По одиночке'], ['По парам']] + back_button, one_time_keyboard=False, resize_keyboard=True)
            self.bot.sendMessage(self.chatId(update), "Как вы хотите продавать билеты?", reply_markup=markup)
            return 6
        if (not update.message.text.replace(" ", "").isdigit()) or (not int(update.message.text.replace(" ", "")) > 0):
            self.notDigitError(update)
            return 7
        
        markup = ReplyKeyboardMarkup(back_button, one_time_keyboard=False, resize_keyboard=True)
        context.user_data['match_ticket_price'] = update.message.text
        self.bot.sendMessage(self.chatId(update), "В объявлении укажите информацию о предложении. Желательно указать:\n-бумажный или электронный билет;\n-готовность встретится лично;\n-готовность к торгу;\n-форма оплаты(нал/бн/крипта);", reply_markup=markup)
        return 8

    def ticket_review(self, update, context):
        if update.message.text == '⬅️Назад':
            markup = ReplyKeyboardMarkup(back_button, one_time_keyboard=False, resize_keyboard=True)
            self.bot.sendMessage(self.chatId(update), "Укажите цену за один билет (Пришлите только число)", reply_markup=markup)
            return 7
        context.user_data['match_ticket_description'] = update.message.text
        markup = ReplyKeyboardMarkup([['Подтвердить']] + back_button, one_time_keyboard=False, resize_keyboard=True)
        ticket_review = f'''Стадия: {context.user_data["match_stage"]}\nДата/Группа: {context.user_data["match_group_or_date"]}\nКатегория: {context.user_data["match_ticket_class"]}\nМатч: {context.user_data["match_name"]}\nВ наличии: {context.user_data["match_tickets_number"]}\nТип продажи: {context.user_data["match_tickets_sell_type"]}\nЦена за шт.: {context.user_data["match_ticket_price"]}\n\nОписание:\n{context.user_data["match_ticket_description"]}'''
        self.bot.sendMessage(self.chatId(update), ticket_review, reply_markup=markup)
        return 9

    def ticket_confirm(self, update, context):
        if update.message.text == '⬅️Назад':
            markup = ReplyKeyboardMarkup(back_button, one_time_keyboard=False, resize_keyboard=True)
            self.bot.sendMessage(self.chatId(update), "В объявлении укажите информацию о предложении. Желательно указать:\n-бумажный или электронный билет;\n-готовность встретится лично;\n-готовность к торгу;\n-форма оплаты(нал/бн/крипта);", reply_markup=markup)
            return 8
        if update.message.text == 'Подтвердить':
            result = self.ticket_functions.create_ticket(context.user_data, update.message.chat_id, str(update.message.from_user.username), update.message.from_user.first_name + ' ' + update.message.from_user.last_name )
            self.bot.sendMessage(self.chatId(update), "Объявление создано", reply_markup=self.main_keyboard)
            return ConversationHandler.END
        else:
            self.bot.sendMessage(self.chatId(update), "Выберите либо 'Подтвердить', либо '⬅️Назад'")
            return 9

    def send_user_listed_tickets(self, update, context):
        listed_tickets = self.ticket_functions.user_listed_tickets(update.message.chat_id)
        if not listed_tickets:
            return ConversationHandler.END
        context.user_data["listed_tickets"] = listed_tickets
        ticket = listed_tickets[0]
        if len(listed_tickets) == 1:
            markup = None
        else:
            keyboard = [
            [
                InlineKeyboardButton("➡️Вперёд", callback_data='forward:1'),
            ]
            ]
            markup = InlineKeyboardMarkup(keyboard)
        r = self.bot.sendMessage(self.chatId(update), f'''<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}''', reply_markup=markup, parse_mode='HTML')
        context.user_data["current_message_id"] = r.message_id
        return 1
    
    def switcher_user_listed_tickets(self, update, context):
        action, ticket_id = update.callback_query.data.split(':')
        self.bot.deleteMessage(update.callback_query.from_user.id, update.callback_query.message.message_id)
        if action == 'forward':
            ticket = context.user_data["listed_tickets"][int(ticket_id)]
            if int(ticket_id) + 1 == len(context.user_data["listed_tickets"]):
                keyboard = [
                [
                    InlineKeyboardButton("⬅️Назад", callback_data=f'back:{int(ticket_id) - 1}'),
                ]
                ]
            else:
                keyboard = [
                [
                    InlineKeyboardButton("⬅️Назад", callback_data=f'back:{int(ticket_id) - 1}'),
                    InlineKeyboardButton("➡️Вперёд", callback_data=f'forward:{int(ticket_id) + 1}'),
                ]
                ]
            markup = InlineKeyboardMarkup(keyboard)
            r = self.bot.sendMessage(update.callback_query.from_user.id, f'''<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}''', reply_markup=markup, parse_mode='HTML')
            context.user_data["current_message_id"] = r.message_id
        if action == 'back':
            ticket = context.user_data["listed_tickets"][int(ticket_id)]
            if int(ticket_id) == 0:
                keyboard = [
                [
                    InlineKeyboardButton("➡️Вперёд", callback_data=f'forward:{int(ticket_id) + 1}'),
                ]
                ]
            else:
                keyboard = [
                [
                    InlineKeyboardButton("⬅️Назад", callback_data=f'back:{int(ticket_id) - 1}'),
                    InlineKeyboardButton("➡️Вперёд", callback_data=f'forward:{int(ticket_id) + 1}'),
                ]
                ]
            markup = InlineKeyboardMarkup(keyboard)
            r = self.bot.sendMessage(update.callback_query.from_user.id, f'''<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}''', reply_markup=markup, parse_mode='HTML')
            context.user_data["current_message_id"] = r.message_id
        return 1

    def stop_callback_conversation(self, update, context):
        if len(context.user_data["listed_tickets"]) > 1:
            self.bot.editMessageReplyMarkup(self.chatId(update), context.user_data["current_message_id"], reply_markup=None)
        self.bot.sendMessage(self.chatId(update), "Просмотр билетов завершён", reply_markup=self.main_keyboard)
        return ConversationHandler.END

    def stop(self, update, context):
        return ConversationHandler.END 