from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from .MatchFunctionsFile import MatchFunctions
from .TicketFunctionsFile import TicketFunctions
from .UserFunctionsFile import UserFunctions

back_button = [['Назад']]

class SellerFunctions(UserFunctions):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.match_functions = MatchFunctions()
        self.ticket_functions = TicketFunctions()
        self.main_keyboard = ReplyKeyboardMarkup([['Купить', 'Продать'], ['Мои объявления'], ['Мой профиль', 'Оценить пользователя'], ['Тех-поддержка']], one_time_keyboard=False, resize_keyboard=True)
        print('UserFunctions connected')

    # Функции Класса
    def match_tickets_sell_type(self, update, context):
        if not update.message.text.isdigit():
            self.notDigitError(update)
            return 5

        markup = ReplyKeyboardMarkup([['По одиночке'], ['По парам']], one_time_keyboard=False, resize_keyboard=True)
        context.user_data['match_tickets_number'] = update.message.text
        self.bot.sendMessage(self.chatId(update), "Как вы хотите продавать билеты?", reply_markup=markup)
        return 6
        
    def match_ticket_price(self, update, context):
        if not update.message.text in ['По одиночке', 'По парам']:
            self.notKeyboardShortcutError(update)
            return 6

        markup = ReplyKeyboardMarkup(back_button, one_time_keyboard=False, resize_keyboard=True)
        context.user_data['match_tickets_sell_type'] = update.message.text
        self.bot.sendMessage(self.chatId(update), "Укажите цену за один билет (Пришлите только число)", reply_markup=markup)
        return 7
    
    def match_ticket_description(self, update, context):
        if not update.message.text.replace(" ", "").isdigit():
            self.notDigitError(update)
            return 7
        
        markup = ReplyKeyboardMarkup(back_button, one_time_keyboard=False, resize_keyboard=True)
        context.user_data['match_ticket_price'] = update.message.text
        self.bot.sendMessage(self.chatId(update), "В объявлении укажите информацию о предложении. Желательно указать:\n-бумажный или электронный билет;\n-готовность встретится лично;\n-готовность к торгу;\n-форма оплаты(нал/бн/крипта);", reply_markup=markup)
        return 8

    def ticket_review(self, update, context):
        context.user_data['match_ticket_description'] = update.message.text
        markup = ReplyKeyboardMarkup([['Подтвердить']] + back_button, one_time_keyboard=False, resize_keyboard=True)
        ticket_review = f'''Стадия: {context.user_data["match_stage"]}\nДата/Группа: {context.user_data["match_group_or_date"]}\nКатегория: {context.user_data["match_ticket_class"]}\nВ наличии: {context.user_data["match_tickets_number"]}\nТип продажи: {context.user_data["match_tickets_sell_type"]}\nЦена за шт.: {context.user_data["match_ticket_price"]}'''
        self.bot.sendMessage(self.chatId(update), ticket_review, reply_markup=markup)
        return 9

    def ticket_confirm(self, update, context):
        result = self.ticket_functions.create_ticket(context.user_data, update.message.chat_id, str(update.message.from_user.username))
        self.bot.sendMessage(self.chatId(update), "Объявление создано", reply_markup=self.main_keyboard)
        return ConversationHandler.END

    def send_user_listed_tickets(self, update, context):
        print(context)
        listed_tickets = self.ticket_functions.user_listed_tickets(update.message.chat_id)
        if not listed_tickets:
            print("Вы пока не выставили на продажу ни одного билета!")
            return ConversationHandler.END
        context.user_data["listed_tickets"] = listed_tickets
        ticket = listed_tickets[0]
        if len(listed_tickets) == 1:
            markup = None
        else:
            keyboard = [
            [
                InlineKeyboardButton("Вперёд", callback_data='forward:0'),
            ]
            ]
            markup = InlineKeyboardMarkup(keyboard)
        r = self.bot.sendMessage(self.chatId(update), f'''Стадия: {ticket[3]}\nДата/Группа: {ticket[4]}\nКатегория: {ticket[5]}\nВ наличии: {ticket[6]}\nМинимум к продаже: {ticket[7]}\nЦена за шт.: {ticket[8]}''', reply_markup=markup)
        context.user_data["current_message_id"] = r.message_id
        return 1
    
    def switcher_user_listed_tickets(self, update, context):
        action, ticket_id = update.callback_query.data.split(':')
        self.bot.deleteMessage(update.callback_query.from_user.id, update.callback_query.message.message_id)
        if action == 'forward':
            ticket = context.user_data["listed_tickets"][int(ticket_id) + 1]
            if int(ticket_id) + 1 == len(context.user_data["listed_tickets"]) - 1:
                keyboard = [
                [
                    InlineKeyboardButton("Назад", callback_data=f'back:{int(ticket_id) + 1}'),
                ]
                ]
            else:
                keyboard = [
                [
                    InlineKeyboardButton("Назад", callback_data=f'back:{int(ticket_id) + 1}'),
                    InlineKeyboardButton("Вперёд", callback_data=f'forward:{int(ticket_id) + 1}'),
                ]
                ]
            markup = InlineKeyboardMarkup(keyboard)
            r = self.bot.sendMessage(update.callback_query.from_user.id, f'''Стадия: {ticket[3]}\nДата/Группа: {ticket[4]}\nКатегория: {ticket[5]}\nВ наличии: {ticket[6]}\nМинимум к продаже: {ticket[7]}\nЦена за шт.: {ticket[8]}''', reply_markup=markup)
            context.user_data["current_message_id"] = r.message_id
        if action == 'back':
            ticket = context.user_data["listed_tickets"][int(ticket_id) - 1]
            if int(ticket_id) - 1 == 0:
                keyboard = [
                [
                    InlineKeyboardButton("Вперёд", callback_data=f'forward:{int(ticket_id) - 1}'),
                ]
                ]
            else:
                keyboard = [
                [
                    InlineKeyboardButton("Назад", callback_data=f'back:{int(ticket_id) - 1}'),
                    InlineKeyboardButton("Вперёд", callback_data=f'forward:{int(ticket_id) - 1}'),
                ]
                ]
            markup = InlineKeyboardMarkup(keyboard)
            r = self.bot.sendMessage(update.callback_query.from_user.id, f'''Стадия: {ticket[3]}\nДата/Группа: {ticket[4]}\nКатегория: {ticket[5]}\nВ наличии: {ticket[6]}\nМинимум к продаже: {ticket[7]}\nЦена за шт.: {ticket[8]}''', reply_markup=markup)
            context.user_data["current_message_id"] = r.message_id
        return 1

    def stop_callback_conversation(self, update, context):
        if len(context.user_data["listed_tickets"]) > 1:
            self.bot.editMessageReplyMarkup(self.chatId(update), context.user_data["current_message_id"], reply_markup=None)
        self.bot.sendMessage(self.chatId(update), "Просмотр билетов завершён", reply_markup=self.main_keyboard)
        return ConversationHandler.END

    def stop(self, update, context):
        return ConversationHandler.END 