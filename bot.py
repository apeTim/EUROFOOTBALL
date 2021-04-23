from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from classes.BotMainFunctionsFile import BotMainFunctions
from classes.ConversationScenariosFile import ConversationScenarios

def main():
    updater = Updater('1708143492:AAFwkcrw6VYrem2d_q4hta4-HgfTGT45XHI', use_context=True)
    bot = Bot('1708143492:AAFwkcrw6VYrem2d_q4hta4-HgfTGT45XHI')
    dp = updater.dispatcher

    conversation_scenario = ConversationScenarios(bot)
    bot_functions = BotMainFunctions()


    dp.add_handler(CommandHandler("start", bot_functions.start_command))
    dp.add_handler(conversation_scenario.user_listings_scenario())
    dp.add_handler(conversation_scenario.seller_conversation_scenario())
    dp.add_handler(conversation_scenario.buyer_conversation_scenario())
    dp.add_handler(MessageHandler(Filters.text, bot_functions.any_text))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()