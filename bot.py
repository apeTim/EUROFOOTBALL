from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from classes.BotMainFunctionsFile import BotMainFunctions
from classes.UserFunctionsFile import UserFunctions
from classes.ConversationScenariosFile import ConversationScenarios

def main():
    updater = Updater('1774407270:AAF3LU2rQt8b3VIRY9BKn7p0v0ZwdDWsGt8', use_context=True)
    bot = Bot('1774407270:AAF3LU2rQt8b3VIRY9BKn7p0v0ZwdDWsGt8')
    dp = updater.dispatcher

    conversation_scenario = ConversationScenarios(bot)
    bot_functions = BotMainFunctions()
    user_functions = UserFunctions(bot)

    dp.add_handler(CommandHandler("start", bot_functions.start_command))
    dp.add_handler(conversation_scenario.user_listings_scenario())
    dp.add_handler(conversation_scenario.seller_conversation_scenario())
    dp.add_handler(conversation_scenario.buyer_conversation_scenario())
    dp.add_handler(conversation_scenario.rate_user_scenario())
    dp.add_handler(MessageHandler(Filters.regex("👤Мой профиль"), user_functions.user_profile))
    dp.add_handler(MessageHandler(Filters.regex("✉️Тех-поддержка"), bot_functions.send_contacts))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()