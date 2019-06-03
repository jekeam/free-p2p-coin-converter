import sys
import traceback
import logging

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, RegexHandler
from telegram.error import BadRequest
from telegram.ext.callbackcontext import CallbackContext

import conf
import dict_word
import bot_util

CURR_LANG = 'RU'

def start(update, context):
    reset_user_data(context)
    update.message.reply_text(text=dict_word.start.get(CURR_LANG))
    
def set_choice(choice, val):
    pass

def get_choice(choice, val):
    pass

def reset_user_data(context):
    for key , val in context.user_data.items():
        print(key + '(' + str(val) + ')->' + str(None))
        key = None


def error_callback(bot, update, error):
    try:
        raise error
    # except Unauthorized:
    #     # remove update.message.chat_id from conversation list
    except BadRequest as e:
        print('BadRequest: ' + str(e))
        # handle malformed requests - read more below!
    # except TimedOut:
    #     # handle slow connection problems
    # except NetworkError:
    #     # handle other connection problems
    # except ChatMigrated as e:
    #     # the chat_id of a group has changed, use e.new_chat_id instead
    # except TelegramError:
    #     # handle all other telegram related errors


logging.basicConfig(filename='bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    updater = Updater(conf.TOKEN, use_context=True, request_kwargs=conf.REQUEST_KWARGS)
    dispatcher = updater.dispatcher
    context = CallbackContext(dispatcher)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('restart', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error_callback)
    # updater.dispatcher.add_handler(CallbackQueryHandler(button))
    # updater.dispatcher.add_handler(MessageHandler(Filters.text, add_address))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
