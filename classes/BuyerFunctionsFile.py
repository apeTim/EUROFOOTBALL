from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from .MatchFunctionsFile import MatchFunctions
from .TicketFunctionsFile import TicketFunctions
from .UserFunctionsFile import UserFunctions

back_button = [['Назад']]

menu_button = [['В главное меню']]

MATCH_TICKET_CLASSES = [['1', '2', '3'], ['1OV', '2OV', '3OV'], ['VIP']]

class BuyerFunctions(UserFunctions):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.match_functions = MatchFunctions()
        self.ticket_functions = TicketFunctions()
        print('UserFunctions connected')
        
    def send_needed_tickets(self, update, context):
        if update.message.text == 'Назад':
            markup = ReplyKeyboardMarkup(MATCH_TICKET_CLASSES + back_button, one_time_keyboard=False, resize_keyboard=True)
            self.bot.sendMessage(self.chatId(update), "Выберите категорию билета", reply_markup=markup)
            return 4
        if (not update.message.text.isdigit()) or (not int(update.message.text.replace(" ", "")) > 0):
            self.notKeyboardShortcutError(update)
            return 5

        context.user_data["match_tickets_number"] = update.message.text
        needed_tickets = self.ticket_functions.user_needed_tickets(self.chatId(update), context.user_data)
        if not needed_tickets:
            self.bot.sendMessage(self.chatId(update), "К сожалению пока нет билетов по вашим параметров", reply_markup=self.main_keyboard)
            return ConversationHandler.END
        print(needed_tickets)
        context.user_data["needed_tickets"] = needed_tickets
        ticket = needed_tickets[0]
        if len(needed_tickets) == 1:
            markup = None
        else:
            keyboard = [
            [
                InlineKeyboardButton("Вперёд", callback_data='forward:0'),
            ]
            ]
            markup = InlineKeyboardMarkup(keyboard)
        r = self.bot.sendMessage(self.chatId(update), f'''<b>Продавец:</b> @{ticket[2]}\n<b>Рейтинг:</b> {ticket[11]}\n\n<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}''', reply_markup=markup, parse_mode='HTML')
        context.user_data["current_message_id"] = r.message_id
        return 6
    
    def switcher_needed_tickets(self, update, context):
        action, ticket_id = update.callback_query.data.split(':')
        self.bot.deleteMessage(update.callback_query.from_user.id, update.callback_query.message.message_id)
        if action == 'forward':
            ticket = context.user_data["needed_tickets"][int(ticket_id) + 1]
            if int(ticket_id) + 1 == len(context.user_data["needed_tickets"]) - 1:
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
            r = self.bot.sendMessage(update.callback_query.from_user.id, f'''<b>Продавец:</b> @{ticket[2]}\n<b>Рейтинг:</b> {ticket[11]}\n\n<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}''', reply_markup=markup, parse_mode='HTML')
            context.user_data["current_message_id"] = r.message_id
        if action == 'back':
            ticket = context.user_data["needed_tickets"][int(ticket_id) - 1]
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
            r = self.bot.sendMessage(update.callback_query.from_user.id, f'''<b>Продавец:</b> @{ticket[2]}\n<b>Рейтинг:</b> {ticket[11]}\n\n<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}''', reply_markup=markup, parse_mode='HTML')
            context.user_data["current_message_id"] = r.message_id
        return 6
    
    def switcher_user_listed_tickets(self, update, context):
        action, ticket_id = update.callback_query.data.split(':')
        self.bot.deleteMessage(update.callback_query.from_user.id, update.callback_query.message.message_id)
        if action == 'forward':
            ticket = context.user_data["needed_tickets"][int(ticket_id) + 1]
            if int(ticket_id) + 1 == len(context.user_data["needed_tickets"]) - 1:
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
            r = self.bot.sendMessage(update.callback_query.from_user.id, f'''<b>Продавец:</b> @{ticket[2]}\n<b>Рейтинг:</b> {ticket[11]}\n\n<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}''', reply_markup=markup, parse_mode='HTML')
            context.user_data["current_message_id"] = r.message_id
        if action == 'back':
            ticket = context.user_data["needed_tickets"][int(ticket_id) - 1]
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
            r = self.bot.sendMessage(update.callback_query.from_user.id, f'''<b>Продавец:</b> @{ticket[2]}\n<b>Рейтинг:</b> {ticket[11]}\n\n<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}''', reply_markup=markup, parse_mode='HTML')
            context.user_data["current_message_id"] = r.message_id
        return 1

    def stop_callback_conversation(self, update, context):
        if len(context.user_data["needed_tickets"]) > 1:
           self.bot.editMessageReplyMarkup(self.chatId(update), context.user_data["current_message_id"], reply_markup=None)
        self.bot.sendMessage(self.chatId(update), "Просмотр билетов завершён", reply_markup=self.main_keyboard)
        return ConversationHandler.END

    def stop(self, update, context):
        return ConversationHandler.END 