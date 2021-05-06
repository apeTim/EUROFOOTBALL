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
            result = self.ticket_functions.create_ticket(context.user_data, update.message.chat_id, update.message.from_user.first_name + ' ' + update.message.from_user.last_name )
            self.bot.sendMessage(self.chatId(update), "Объявление создано", reply_markup=self.main_keyboard)
            return ConversationHandler.END
        else:
            self.bot.sendMessage(self.chatId(update), "Выберите либо 'Подтвердить', либо '⬅️Назад'")
            return 9

    def send_user_listed_tickets(self, update, context):
        listed_tickets = self.ticket_functions.user_listed_tickets(update.message.chat_id)
        if not listed_tickets:
            return ConversationHandler.END
        context.user_data["listed_tickets"] = [list(x) for x in listed_tickets]
        ticket = listed_tickets[0]
        if len(listed_tickets) == 1:
            keyboard = [
            [
                InlineKeyboardButton("🗑️Удалить", callback_data='delete:0'),
                InlineKeyboardButton("✏️Редактировать", callback_data='edit:0')
            ]
            ]
        else:
            keyboard = [
            [
                InlineKeyboardButton("➡️Вперёд", callback_data='forward:1'),
            ],
            [
                InlineKeyboardButton("🗑️Удалить", callback_data='delete:0'),
                InlineKeyboardButton("✏️Редактировать", callback_data='edit:0')
            ]
            ]
            markup = InlineKeyboardMarkup(keyboard)
        r = self.bot.sendMessage(self.chatId(update), f'''<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}''', reply_markup=markup, parse_mode='HTML')
        context.user_data["current_message_id"] = r.message_id
        context.user_data["current_reply_markup"] = markup
        return 1
    
    def edit_message_chooser(self, update, context):
        action, ticket_id = update.callback_query.data.split(':')
        if action == 'edit_sell_type':
            markup = ReplyKeyboardMarkup([['По одиночке'], ['По парам']] + back_button, one_time_keyboard=False, resize_keyboard=True)
            self.bot.sendMessage(update.callback_query.from_user.id, 'Выберите новый тип продажи билетов', reply_markup=markup)
            context.user_data["edit_field"] = 'sell_type'
            return 3
        elif action == 'edit_price':
            self.bot.sendMessage(update.callback_query.from_user.id, 'Пришлите новую цену билета')
            context.user_data["edit_field"] = 'price'
            return 3
        elif action == 'edit_description':
            self.bot.sendMessage(update.callback_query.from_user.id, 'Пришлите новое описание')
            context.user_data["edit_field"] = 'description'
            return 3
        elif action == 'go_back':
            ticket = context.user_data["listed_tickets"][int(ticket_id)]
            message_text =  f'''<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}'''
            self.bot.editMessageText(message_text, chat_id=update.callback_query.from_user.id, message_id=context.user_data["current_message_id"], reply_markup=context.user_data["current_reply_markup"], parse_mode='HTML')
            return 1

    
    def edit_message(self, update, context):
        current_ticket_id = context.user_data["current_ticket_id"]
        edit_field = context.user_data["edit_field"]
        message_text = update.message.text
        if edit_field == 'sell_type':
            if message_text not in ['По одиночке', 'По парам']:
                markup = ReplyKeyboardMarkup([['По одиночке'], ['По парам']] + back_button, one_time_keyboard=False, resize_keyboard=True)
                self.bot.sendMessage(self.chatId(update), 'Для выбора используйте только клавиатуру!', reply_markup=markup)
                return 3
            context.user_data["listed_tickets"][int(current_ticket_id)][8] = message_text
            ticket_id = context.user_data["listed_tickets"][int(current_ticket_id)][0]
            self.ticket_functions.edit_ticket(ticket_id, 'match_tickets_sell_type', message_text)
        elif edit_field == 'price':
            if (not message_text.isdigit()) or (int(message_text) < 0) :
                self.bot.sendMessage(self.chatId(update), 'Вы прислали неверное число')
                return 3
            context.user_data["listed_tickets"][int(current_ticket_id)][9] = message_text
            ticket_id = context.user_data["listed_tickets"][int(current_ticket_id)][0]
            self.ticket_functions.edit_ticket(ticket_id, 'match_ticket_price', message_text)
        elif edit_field == 'description':
            context.user_data["listed_tickets"][int(current_ticket_id)][10] = message_text
            ticket_id = context.user_data["listed_tickets"][int(current_ticket_id)][0]
            self.ticket_functions.edit_ticket(ticket_id, 'match_ticket_description', message_text)
        ticket = context.user_data["listed_tickets"][int(current_ticket_id)]
        message_text =  f'''<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}'''
        self.bot.editMessageReplyMarkup(self.chatId(update), context.user_data["current_message_id"], reply_markup=None)
        self.bot.sendMessage(self.chatId(update), 'Объявление изменено', reply_markup=self.main_keyboard)
        r = self.bot.sendMessage(self.chatId(update), message_text, reply_markup=context.user_data["current_reply_markup"], parse_mode='HTML')
        context.user_data["current_message_id"] = r.message_id
        return 1


    def switcher_user_listed_tickets(self, update, context):
        action, ticket_id = update.callback_query.data.split(':')
        context.user_data["current_ticket_id"] = ticket_id
        if action == 'edit':
            ticket = context.user_data["listed_tickets"][int(ticket_id)]
            if ticket == 'deleted':
                self.bot.answerCallbackQuery(update.callback_query.id, text='Нельзя редактировать удалённое объявление')
                return 1
            keyboard = [
            [
                InlineKeyboardButton("Редактировать Тип Продажи", callback_data=f'edit_sell_type:{int(ticket_id)}')
            ],
            [
                InlineKeyboardButton("Редактировать Цену билета", callback_data=f'edit_price:{int(ticket_id)}')
            ],
            [
                InlineKeyboardButton("Редактировать Описание", callback_data=f'edit_description:{int(ticket_id)}')
            ],
            [
                InlineKeyboardButton("Назад", callback_data=f'go_back:{int(ticket_id)}')
            ],
            ]
            markup = InlineKeyboardMarkup(keyboard)
            self.bot.editMessageReplyMarkup(update.callback_query.from_user.id, context.user_data["current_message_id"], reply_markup=markup)
            return 2

        elif action == 'delete':
            keyboard = [
            [
                InlineKeyboardButton("🗑️Удалить", callback_data=f'delete_confirm:{int(ticket_id)}'),
                InlineKeyboardButton("🔁Отменить", callback_data=f'delete_cancel:{int(ticket_id)}'),
            ]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            self.bot.editMessageText('Вы действительно хотите удалить данный билет?\nОтменить данное действие будет невозможно', chat_id=update.callback_query.from_user.id, message_id=context.user_data["current_message_id"], reply_markup=markup)
        elif action == 'delete_confirm':
            ticket = context.user_data["listed_tickets"][int(ticket_id)]
            db_ticket_id = ticket[0]
            context.user_data["listed_tickets"][int(ticket_id)] = 'deleted'
            self.ticket_functions.delete_ticket_by_id(db_ticket_id)
            self.bot.editMessageText('Данное объявление удалено', chat_id=update.callback_query.from_user.id, message_id=context.user_data["current_message_id"], reply_markup=context.user_data["current_reply_markup"])
        elif action == 'delete_cancel':
            ticket = context.user_data["listed_tickets"][int(ticket_id)]
            message_text =  f'''<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}'''
            self.bot.editMessageText(message_text, chat_id=update.callback_query.from_user.id, message_id=context.user_data["current_message_id"], reply_markup=context.user_data["current_reply_markup"], parse_mode='HTML')
        elif action == 'forward':
            self.bot.deleteMessage(update.callback_query.from_user.id, update.callback_query.message.message_id)
            ticket = context.user_data["listed_tickets"][int(ticket_id)]
            if int(ticket_id) + 1 == len(context.user_data["listed_tickets"]):
                keyboard = [
                [
                    InlineKeyboardButton("⬅️Назад", callback_data=f'back:{int(ticket_id) - 1}'),
                ],
                [
                    InlineKeyboardButton("🗑️Удалить", callback_data=f'delete:{int(ticket_id)}'),
                    InlineKeyboardButton("✏️Редактировать", callback_data=f'edit:{int(ticket_id)}')
                ]
                ]
            else:
                keyboard = [
                [
                    InlineKeyboardButton("⬅️Назад", callback_data=f'back:{int(ticket_id) - 1}'),
                    InlineKeyboardButton("➡️Вперёд", callback_data=f'forward:{int(ticket_id) + 1}'),
                ],
                [
                    InlineKeyboardButton("🗑️Удалить", callback_data=f'delete:{int(ticket_id)}'),
                    InlineKeyboardButton("✏️Редактировать", callback_data=f'edit:{int(ticket_id)}')
                ]
                ]
            markup = InlineKeyboardMarkup(keyboard)
            if ticket == 'deleted':
                message_text = 'Данное объявление удалено'
            else:
                message_text =  f'''<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}'''
            r = self.bot.sendMessage(update.callback_query.from_user.id, message_text, reply_markup=markup, parse_mode='HTML')
            context.user_data["current_message_id"] = r.message_id
            context.user_data["current_reply_markup"] = markup
        elif action == 'back':
            self.bot.deleteMessage(update.callback_query.from_user.id, update.callback_query.message.message_id)
            ticket = context.user_data["listed_tickets"][int(ticket_id)]
            if int(ticket_id) == 0:
                keyboard = [
                [
                    InlineKeyboardButton("➡️Вперёд", callback_data=f'forward:{int(ticket_id) + 1}'),
                ],
                [
                    InlineKeyboardButton("🗑️Удалить", callback_data=f'delete:{int(ticket_id)}'),
                    InlineKeyboardButton("✏️Редактировать", callback_data=f'edit:{int(ticket_id)}')
                ]
                ]
            else:
                keyboard = [
                [
                    InlineKeyboardButton("⬅️Назад", callback_data=f'back:{int(ticket_id) - 1}'),
                    InlineKeyboardButton("➡️Вперёд", callback_data=f'forward:{int(ticket_id) + 1}'),
                ],
                [
                    InlineKeyboardButton("🗑️Удалить", callback_data=f'delete:{int(ticket_id)}'),
                    InlineKeyboardButton("✏️Редактировать", callback_data=f'edit:{int(ticket_id)}')
                ]
                ]
            markup = InlineKeyboardMarkup(keyboard)
            if ticket == 'deleted':
                message_text = 'Данное объявление удалено'
            else:
                message_text =  f'''<b>Стадия:</b> {ticket[3]}\n<b>Дата/Группа:</b> {ticket[4]}\n<b>Матч:</b> {ticket[5]}\n<b>Категория билета:</b> {ticket[6]}\n<b>Кол-во билетов:</b> {ticket[7]}\n<b>Тип продажи:</b> {ticket[8]}\n<b>Цена за шт.:</b> {ticket[9]}\n\n<b>Описание:</b>\n{ticket[10]}'''
            r = self.bot.sendMessage(update.callback_query.from_user.id, message_text, reply_markup=markup, parse_mode='HTML')
            context.user_data["current_message_id"] = r.message_id
            context.user_data["current_reply_markup"] = markup
        return 1

    def stop_callback_conversation(self, update, context):
        if len(context.user_data["listed_tickets"]) > 1:
            self.bot.editMessageReplyMarkup(self.chatId(update), context.user_data["current_message_id"], reply_markup=None)
        self.bot.sendMessage(self.chatId(update), "Просмотр билетов завершён", reply_markup=self.main_keyboard)
        return ConversationHandler.END

    def stop(self, update, context):
        return ConversationHandler.END 