from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, CallbackQueryHandler
from .SellerFunctionsFile import SellerFunctions
from .BotMainFunctionsFile import BotMainFunctions
from .TicketFunctionsFile import TicketFunctions
from .BuyerFunctionsFile import BuyerFunctions
from .UserFunctionsFile import UserFunctions
from .AdminFunctionsFile import AdminFunctions

class ConversationScenarios:
    def __init__(self, bot):
        self.bot = bot
        self.user_functions = UserFunctions(bot=bot)
        self.seller_functions = SellerFunctions(bot)
        self.buyer_functions = BuyerFunctions(bot)
        self.bot_functions = BotMainFunctions()
        self.ticket_functions = TicketFunctions()
        self.admin_functions = AdminFunctions(bot)
     
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
                2: [CallbackQueryHandler(self.seller_functions.edit_message_chooser, pass_user_data=True)],
                3: [MessageHandler(Filters.text, self.seller_functions.edit_message, pass_user_data=True)],

            },
            fallbacks=[MessageHandler(Filters.text, self.seller_functions.stop_callback_conversation)]
        )
        return user_listings_scenario

    def trust_user_scenario(self):
        trust_user_scenario = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('🌟Оценить пользователя'), self.user_functions.trust_user_nickname, pass_user_data=True)],
            states={
                1: [MessageHandler(Filters.text, self.user_functions.trust_user_relationships, pass_user_data=True)],
                2: [MessageHandler(Filters.text, self.user_functions.trust_user_trust, pass_user_data=True)],
                3: [MessageHandler(Filters.text, self.user_functions.trust_user_end, pass_user_data=True)]
            },
            fallbacks=[MessageHandler(Filters.regex('🏠В главное меню'), self.user_functions.stop_conversation)]
        )
        return trust_user_scenario
    
    def user_profile_scenario(self):
        user_profile_scenario = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex("👤Мой профиль"), self.user_functions.user_profile)],
            states={
                1: [MessageHandler(Filters.text, self.user_functions.choose_profile_action, pass_user_data=True)],
                2: [MessageHandler(Filters.photo, self.user_functions.picture_sent, pass_user_data=True)],
            },
            fallbacks=[MessageHandler(Filters.regex('🏠В главное меню'), self.user_functions.stop_conversation)]
        )
        return user_profile_scenario
    
    def admin_verification_scenario(self):
        admin_verification_scenario = ConversationHandler(
            entry_points=[CommandHandler("admin_vrf", self.admin_functions.verificate_users, pass_user_data=True)],
            states={
                1: [CallbackQueryHandler(self.admin_functions.switcher_verificate_users, pass_user_data=True)],
            },
            fallbacks=[CommandHandler("opop", self.admin_functions.verificate_users)]
        )
        return admin_verification_scenario