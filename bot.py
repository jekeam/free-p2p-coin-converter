import sys
import traceback
import logging

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, RegexHandler
from telegram.error import BadRequest
from telegram.ext.callbackcontext import CallbackContext

# from emoji import emojize

import conf
import dict_word
import bot_util

CURR_LANG = 'RU'

ROAD_MAP = {
    'choice_coin_sell': 'choice_addr_sell',
    'choice_addr_sell': 'choice_sum',
    'choice_sum': 'choice_coin_buy',
    'choice_coin_buy': 'choice_addr_buy',
    'choice_addr_buy': 'request_list'
}


def bild_inline_btn(message, btn:dict, text:str):
    kb = []
    for key, val in btn.items():
        kb.append([InlineKeyboardButton(text=val, callback_data=key)])
    reply_markup = InlineKeyboardMarkup(kb)
    message.reply_text(text=text, reply_markup=reply_markup)


def get_coins_dict(exclude=None):
    coins = {}
    for c in conf.accsess_coins:
        coins[c] = c
    if exclude:
        coins.pop(exclude)
    return coins

def start(update, context):
    reset_user_data(context)
    coins = get_coins_dict()
    bild_inline_btn(update.message, coins, 'Пожалуйста выбере монету, которую вы хотите продать:')
    set_(context, 'step', 'choice_coin_sell')
    
    
def set_(context, param:str, val:str):
    context.user_data[param] = val
    
def get_(context, param:str):
    return context.user_data.get(param)
    
def get_next_step(context):
    global ROAD_MAP
    return ROAD_MAP.get(get_(context, 'step'))    
    
def set_next_step(context):
    global ROAD_MAP
    next_step = get_next_step(context)
    print('old step: {}, current: {}'.format(get_(context, 'step'), next_step))
    set_(context, 'step', next_step)
    
    
def inline_manager(update, context):
    step = get_(context, 'step')
    
    # data = None
    # try:
    data = update.callback_query.data
    # except AttributeError:
    #     pass
    
    print('inline_manager, data: {}'.format(data))
    
    if step == 'choice_coin_sell':
        set_(context, 'coin_sell', data)
        update.callback_query.message.reply_text('Пожалуйста, введите адрес для продажи ' + data)
        # TODO: print balance and success mag
    elif step == 'choice_coin_buy':
        set_(context, 'coin_buy', data)
        update.message.reply_text('Пожалуйста, выберете валюту для покупки: ')
        coins = get_coins_dict(get_(context, 'coin_sell'))
        bild_inline_btn(update.callback_query.message, coins, 'Пожалуйста выбере монету, которую вы хотите продать:')
        # TODO: success mag
    
    set_next_step(context)
    
def text_manager(update, context):
    data = update.message.text
    
    print('text_manager, data: {}'.format(data))
    
    if get_(context, 'step') == 'choice_addr_sell':
        set_(context, 'address_sell', data)
        set_next_step(context)
        
    if get_(context, 'step') == 'choice_sum':
        update.message.reply_text('Пожалуйста, введите сумму продажи {}, например: 0.01'.format(get_(context, 'coin_sell')))
        # TODO: success mag
        set_next_step(context)


def reset_user_data(context):
    user_data = context.user_data
    print('user_data: ' + str(user_data))
    if user_data:
        for key , val in user_data.items():
            print(key + ' = ' + str(val) + ' -> clean')
            key = None
    else:
        print('context.user_data is empty')


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
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    updater = Updater(conf.TOKEN, use_context=True, request_kwargs=conf.REQUEST_KWARGS)
    dispatcher = updater.dispatcher
    context = CallbackContext(dispatcher)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('restart', start))
    # updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error_callback)
    updater.dispatcher.add_handler(CallbackQueryHandler(inline_manager))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, text_manager))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
