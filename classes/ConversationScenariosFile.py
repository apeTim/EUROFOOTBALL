from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, CallbackQueryHandler
from .SellerFunctionsFile import SellerFunctions
from .BotMainFunctionsFile import BotMainFunctions
from .TicketFunctionsFile import TicketFunctions
from .BuyerFunctionsFile import BuyerFunctions
from .UserFunctionsFile import UserFunctions

class ConversationScenarios:
    def __init__(self, bot):
        self.bot = bot
        self.user_functions = UserFunctions(bot=bot)
        self.seller_functions = SellerFunctions(bot)
        self.buyer_functions = BuyerFunctions(bot)
        self.bot_functions = BotMainFunctions()
        self.ticket_functions = TicketFunctions()
     
    def seller_conversation_scenario(self):
        seller_conversation_scenario = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('💰Продать'), self.seller_functions.choose_match_stage)],
            states={
                1: [MessageHandler(Filters.text, self.seller_functions.choose_match_date, pass_user_data=True)],
                2: [MessageHandler(Filters.text, self.seller_functions.choose_match_name, pass_user_data=True)],
                3: [MessageHandler(Filters.text, self.seller_functions.choose_match_ticket_class, pass_user_data=True)],
                4: [MessageHandler(Filters.text, self.seller_functions.choose_match_tickets_number, pass_user_data=True)],
                5: [MessageHandler(Filters.text, self.seller_functions.match_tickets_sell_type, pass_user_data=True)],
                6: [MessageHandler(Filters.text, self.seller_functions.match_ticket_price, pass_user_data=True)],
                7: [MessageHandler(Filters.text, self.seller_functions.match_ticket_description, pass_user_data=True)],
                8: [MessageHandler(Filters.text, self.seller_functions.ticket_review, pass_user_data=True)],
                9: [MessageHandler(Filters.text, self.seller_functions.ticket_confirm, pass_user_data=True)],
            },
            fallbacks=[MessageHandler(Filters.regex('🏠В главное меню'), self.bot_functions.stop_conversation)]
        )
        return seller_conversation_scenario

    def buyer_conversation_scenario(self):
        buyer_conversation_scenario = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('🛒Купить'), self.buyer_functions.choose_match_stage)],
            states={
                1: [MessageHandler(Filters.text, self.buyer_functions.choose_match_date, pass_user_data=True)],
                2: [MessageHandler(Filters.text, self.buyer_functions.choose_match_name, pass_user_data=True)],
                3: [MessageHandler(Filters.text, self.buyer_functions.choose_match_ticket_class, pass_user_data=True)],
                4: [MessageHandler(Filters.text, self.buyer_functions.choose_match_tickets_number, pass_user_data=True)],
                5: [MessageHandler(Filters.text, self.buyer_functions.send_needed_tickets, pass_user_data=True)],
                6: [CallbackQueryHandler(self.buyer_functions.switcher_needed_tickets)]
            },
            fallbacks=[MessageHandler(Filters.regex('🏠В главное меню'), self.buyer_functions.stop_callback_conversation)]
        )
        return buyer_conversation_scenario
    
    def user_listings_scenario(self):
        user_listings_scenario = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('📜Мои объявления'), self.seller_functions.send_user_listed_tickets, pass_user_data=True)],
            states={
                1: [CallbackQueryHandler(self.seller_functions.switcher_user_listed_tickets, pass_user_data=True)],
            },
            fallbacks=[MessageHandler(Filters.text, self.seller_functions.stop_callback_conversation)]
        )
        return user_listings_scenario

    def rate_user_scenario(self):
        rate_user_scenario = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('🌟Оценить пользователя'), self.user_functions.rate_user_nickname, pass_user_data=True)],
            states={
                1: [MessageHandler(Filters.text, self.user_functions.rate_user_relationships, pass_user_data=True)],
                2: [MessageHandler(Filters.text, self.user_functions.rate_user_trust, pass_user_data=True)],
                3: [MessageHandler(Filters.text, self.user_functions.rate_user_end, pass_user_data=True)]
            },
            fallbacks=[MessageHandler(Filters.regex('🏠В главное меню'), self.user_functions.stop_conversation)]
        )
        return rate_user_scenario