from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from classes.BotMainFunctionsFile import BotMainFunctions
from classes.UserFunctionsFile import UserFunctions
from classes.ConversationScenariosFile import ConversationScenarios
import sqlite3

def main():
    updater = Updater('1503161381:AAF4EJ3GadhkiovGrlRtTwLRhv2_D7qhbgQ', use_context=True)
    bot = Bot('1503161381:AAF4EJ3GadhkiovGrlRtTwLRhv2_D7qhbgQ')
    dp = updater.dispatcher

    conversation_scenario = ConversationScenarios(bot)
    bot_functions = BotMainFunctions()
    user_functions = UserFunctions(bot)

    dp.add_handler(conversation_scenario.user_listings_scenario())
    dp.add_handler(conversation_scenario.seller_conversation_scenario())
    dp.add_handler(conversation_scenario.buyer_conversation_scenario())
    dp.add_handler(conversation_scenario.trust_user_scenario())
    dp.add_handler(conversation_scenario.user_profile_scenario())
    dp.add_handler(conversation_scenario.admin_verification_scenario())
    dp.add_handler(MessageHandler(Filters.regex("✉️Тех-поддержка"), bot_functions.send_contacts))
    dp.add_handler(CommandHandler("start", bot_functions.start_command))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()