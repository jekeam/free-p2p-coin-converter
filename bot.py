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
from db_model import create_request, get_requests

CURR_LANG = 'RU'

def send_msg(context, text:str, reply_markup=None):
    user_id = get_(context, 'user_id')
    if user_id:
        if reply_markup:
            context.bot.send_message(user_id, text=text, reply_markup=reply_markup,  parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            context.bot.send_message(user_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)

def choice_coin_sell(context, btn:dict, text:str):
    kb = []
    for key, val in btn.items():
        kb.append([InlineKeyboardButton(text=val, callback_data=key)])
    reply_markup = InlineKeyboardMarkup(kb)
    send_msg(context, text, reply_markup)
    

def get_coins_dict(exclude=None):
    coins = {}
    for c in conf.accsess_coins:
        coins[c] = c
    if exclude:
        try:
            coins.pop(exclude)
        except:
            pass
    return coins


def get_data(update):
    data = None
    try:
        data = update.message.text
    except AttributeError:
        data = update.callback_query.data
    return data
    
def main(update, context):
    data = get_data(update)
    print('main, step: ' + str(get_(context, 'step')) + ', data: ' + str(data))
    
    if 'start' in data:
        reset_user_data(context)
        set_(context, 'step', 'choice_coin_sell')
        
    user_id = None
    try:
        user_id = update.message.from_user.id
    except AttributeError:
        user_id = update.callback_query.from_user.id
    set_(context, 'user_id', user_id)
        
    if get_(context, 'step') == 'choice_coin_sell':
        choice_coin_sell(context, get_coins_dict(), 'Пожалуйста выбере монету, которую вы хотите продать')
        set_(context, 'step', 'set_coin_sell')
    elif get_(context, 'step') == 'set_coin_sell':
        set_(context, 'coin_sell', data)
        set_(context, 'step', 'choice_addr_sell')
        
    if get_(context, 'step') == 'choice_addr_sell':
        send_msg(context, 'Пожалуйста, введите адрес для продажи ' + get_(context, 'coin_sell'))
        set_(context, 'step', 'set_addr_sell')
    elif get_(context, 'step') == 'set_addr_sell':
        set_(context, 'addr_sell', data)
        set_(context, 'step', 'choice_sum')
        
    if get_(context, 'step') == 'choice_sum':
        send_msg(context, 'Пожалуйста, введите сумму продажи {}, например: 0.01'.format(get_(context, 'coin_sell')))
        set_(context, 'step', 'set_sum')
    elif get_(context, 'step') == 'set_sum':
        set_(context, 'sum', data)
        set_(context, 'step', 'choice_coin_buy')
        
    if get_(context, 'step') == 'choice_coin_buy':
        choice_coin_sell(context, get_coins_dict(get_(context, 'coin_sell')), 'Пожалуйста выбере монету, которую вы хотите купить')
        set_(context, 'step', 'set_coin_buy')
    elif get_(context, 'step') == 'set_coin_buy':
        set_(context, 'coin_buy', data)
        set_(context, 'step', 'choice_addr_buy')
        
    if get_(context, 'step') == 'choice_addr_buy':
        send_msg(context, 'Пожалуйста, введите адрес для покупки ' + get_(context, 'coin_buy'))
        set_(context, 'step', 'set_addr_buy')
    elif get_(context, 'step') == 'set_addr_buy':
        set_(context, 'addr_buy', data)
        set_(context, 'step', 'confirm_request')

    if get_(context, 'step') == 'confirm_request':
        kb = []
        kb.append([InlineKeyboardButton(text='Cоздать заявку', callback_data='ok')])
        kb.append([InlineKeyboardButton(text='Отменить', callback_data='restart')])
        reply_markup = InlineKeyboardMarkup(kb)
        send_msg(
            context, 
            'Пожалуйста, проверьте данные:'
            '\nАдрес для продажи {}:\n{}'.format(get_(context, 'coin_sell'), get_(context, 'addr_sell')) + \
            '\nАдрес для покупки {}:\n{}'.format(get_(context, 'coin_buy'), get_(context, 'addr_buy')) + \
            '\nСумма в {}: {}'.format(get_(context, 'coin_sell'), get_(context, 'sum')),
            reply_markup
        )
        set_(context, 'step', 'get_confirm_request')
    elif get_(context, 'step') == 'get_confirm_request':
        if data == 'ok':
            set_(context, 'step', 'create_request')
        
    if get_(context, 'step') == 'create_request':
        create_request(
            get_(context, 'user_id'), 
            get_(context, 'sum'),
            get_(context, 'addr_sell'), 
            get_(context, 'addr_sell'), 
            get_(context, 'coin_buy'), 
            get_(context, 'addr_buy')
        )
        set_(context, 'step', 'show_requests')
        send_msg(context, 'Ваша заявка успешно создана')
    
    if  get_(context, 'step') == 'show_requests' or '/request' == data:
        set_(context, 'step', 'show_requests')
        reuests = get_requests(get_(context, 'user_id'))
        if reuests:
            for reuest in reuests:
                send_msg(context, '*#{}*: {} {} -> {}'.format(reuest.id, reuest.summ, reuest.coin_sell, reuest.coin_buy))
        else:
            send_msg(context, 'Заявок не найдено')
            
        
    
def set_(context, param:str, val:str):
    param = str(param)
    val = str(val)
    print('set_: ' + param + ' = ' + val)
    context.user_data[param] = val
    
    
def get_(context, param:str):
    return context.user_data.get(param)


def reset_user_data(context):
    user_data = context.user_data.copy()
    print('user_data: ' + str(user_data))
    if user_data:
        for key , val in user_data.items():
            print(key + ' = ' + str(val) + ' -> clean')
            context.user_data.pop(key)
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

    updater.dispatcher.add_handler(CommandHandler('start', main))
    updater.dispatcher.add_handler(CommandHandler('restart', main))
    updater.dispatcher.add_handler(CommandHandler('request', main))
    # updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error_callback)
    updater.dispatcher.add_handler(CallbackQueryHandler(main))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, main))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
