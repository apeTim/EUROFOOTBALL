from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from .MatchFunctionsFile import MatchFunctions
from .TicketFunctionsFile import TicketFunctions
from .UserFunctionsFile import UserFunctions
import sqlite3

back_button = [['⬅️Назад']]

menu_button = [['🏠В главное меню']]

MATCH_TICKET_CLASSES = [['1', '2', '3'], ['1OV', '2OV', '3OV'], ['VIP']]

status_emoji = {
    'Актуальное': '✅',
    'Неактуальное': '❌'
}

class BuyerFunctions(UserFunctions):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.match_functions = MatchFunctions()
        self.ticket_functions = TicketFunctions()
        print('UserFunctions connected')
        
    def send_needed_tickets(self, update, context):
        if update.message.text == '⬅️Назад':
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
        context.user_data["needed_tickets"] = [list(x) for x in needed_tickets]
        messages_ids = []
        for index, ticket in enumerate(needed_tickets):
            keyboard = [[InlineKeyboardButton("🗑️Отметить как неактуальное", callback_data=f'expired:{index}')]]
            markup = InlineKeyboardMarkup(keyboard)
            users_who_trusted = "(" + '\n'.join(list(map(lambda x: f"{x[0]} | <a href='tg://user?id={x[3]}'>{x[2]}</a> | 🌟{x[1]}", ticket[16]))) + ")"
            r = self.bot.sendMessage(self.chatId(update), f'''{status_emoji[ticket[11]]}<b>Статус объявления:</b> {ticket[11]}\n\n<b>Продавец:</b> <a href="tg://user?id={ticket[1]}">{ticket[13]}</a>\n<b>Степень доверия:</b> {ticket[14]}\n{users_who_trusted}\n<b>Верификация:</b> {ticket[15]}\n<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}''', reply_markup=markup, parse_mode='HTML')
            messages_ids.append(r.message_id)
        context.user_data["messages_ids"] = messages_ids
        return 6

    def set_listing_to_expired(self, reporter_id, ticket_id):
        with sqlite3.connect('bot.db') as db_connection:
            print("Here!")
            cursor = db_connection.cursor()
            command = f'''SELECT ticket_status FROM tickets WHERE ticket_id = ?'''
            prev_status = cursor.execute(command, (ticket_id,)).fetchone()[0]
            if prev_status == 'Неактуальное':
                return
            command = f'''UPDATE tickets SET ticket_status = "Неактуальное", ticket_status_reporter = ? WHERE ticket_id = ?'''
            cursor.execute( command, (reporter_id, ticket_id, ) )
            db_connection.commit()
            cursor.close() 

    def switcher_needed_tickets(self, update, context):
        action, ticket_id = update.callback_query.data.split(':')
        ticket = context.user_data["needed_tickets"][int(ticket_id)]
        if action == 'expired':
            if ticket[11] == 'Неактуальное':
                self.bot.answerCallbackQuery(update.callback_query.id, text='Объявление уже отмечено, как неактуальное.')
                return 6
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("Подтвердить", callback_data=f"expired_confirm:{ticket_id}"), InlineKeyboardButton("Отменить", callback_data=f"expired_cancel:{ticket_id}")]])
            self.bot.editMessageText("Если Вы уверены что реальная цена не соответствует указанной в объявлении или Продавец отказывается продавать из-за отсутствия в наличии, тогда нажмите- Подтвердить", update.callback_query.from_user.id, context.user_data["messages_ids"][int(ticket_id)], reply_markup=markup)
        elif action == 'expired_confirm':
            self.set_listing_to_expired(update.callback_query.from_user.id, ticket[0])
            self.bot.answerCallbackQuery(update.callback_query.id, text='Объявление отмечено, как неактуальное')
            context.user_data["needed_tickets"][int(ticket_id)][11] = 'Неактуальное'
            keyboard = [[InlineKeyboardButton("🗑️Отметить как неактуальное", callback_data=f'expired:{ticket_id}')]]
            users_who_trusted = "(" + '\n'.join(list(map(lambda x: f"{x[0]} | <a href='tg://user?id={x[3]}'>{x[2]}</a> | 🌟{x[1]}", ticket[16]))) + ")"
            self.bot.editMessageText(f'''{status_emoji['Неактуальное']}<b>Статус объявления:</b> Неактуальное\n\n<b>Продавец:</b> <a href="tg://user?id={ticket[1]}">{ticket[13]}</a>\n<b>Степень доверия:</b> {ticket[14]}\n{users_who_trusted}\n<b>Верификация:</b> {ticket[15]}\n<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}''', update.callback_query.from_user.id, context.user_data["messages_ids"][int(ticket_id)], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        elif action == 'expired_cancel':
            keyboard = [[InlineKeyboardButton("🗑️Отметить как неактуальное", callback_data=f'expired:{ticket_id}')]]
            users_who_trusted = "(" + '\n'.join(list(map(lambda x: f"{x[0]} | <a href='tg://user?id={x[3]}'>{x[2]}</a> | 🌟{x[1]}", ticket[16]))) + ")"
            self.bot.editMessageText(f'''{status_emoji['Актуальное']}<b>Статус объявления:</b> Актуальное\n\n<b>Продавец:</b> <a href="tg://user?id={ticket[1]}">{ticket[13]}</a>\n<b>Степень доверия:</b> {ticket[14]}\n{users_who_trusted}\n<b>Верификация:</b> {ticket[15]}\n<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}''', update.callback_query.from_user.id, context.user_data["messages_ids"][int(ticket_id)], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return 6

    def stop_callback_conversation(self, update, context):
        try:
            for message_id in context.user_data["messages_ids"]:
                self.bot.editMessageReplyMarkup(self.chatId(update), message_id, reply_markup=None)
            self.bot.sendMessage(self.chatId(update), "Просмотр билетов завершён", reply_markup=self.main_keyboard)
            return ConversationHandler.END
        except Exception:
            self.bot.sendMessage(self.chatId(update), "Выход в главное меню", reply_markup=self.main_keyboard)
            return ConversationHandler.END

    def stop(self, update, context):
        return ConversationHandler.END 