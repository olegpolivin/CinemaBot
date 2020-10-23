# -*- coding: utf-8 -*-

import requests
import sys
import telebot
from telebot import types
import time

from cine_quest_lib import config
from cine_quest_lib import cine_quests
from cine_quest_lib.dataloader import Fetcher


bot = telebot.TeleBot(config.token, threaded=False)
fetcher = Fetcher()


@bot.message_handler(commands=['start'])
def handle_start(message):
    """Welcome message
    """
    bot.send_message(message.chat.id, config.start)


@bot.message_handler(commands=['help'])
def command_help(m):
    """Shows help menu
    """
    cid = m.chat.id
    bot.send_message(cid, config.help_text)  # send the generated help page


@bot.message_handler(regexp=r'\/i\d+')
def handle_imdb_id(message):
    """Detect links that start with /i+numbers.
    Allows to call a callback function to show posters and overview.
    """
    try:
        search_id = int(message.json['text'][2:])
        img = fetcher.output[search_id]['poster_path']
        overview = fetcher.output[search_id]['overview']
        fetcher.query = fetcher.output[search_id]['title'][0]
    except Exception:
        msg = 'Что-то пошло не так. Попробуйте еще раз.'
        bot.send_message(message.chat.id, msg)
    if img is not None:
        bot.send_photo(message.chat.id, img)

    if overview:
        bot.send_message(message.chat.id, overview)
    else:
        bot.send_message(message.chat.id, 'Обзора не нашлось')

    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text='Посмотри меня!', callback_data='watch')
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, 'Вот ресурсы, где фильм можно посмотреть.', reply_markup=keyboard)

# Обычный режим
@bot.message_handler(content_types=["text"])
def any_msg(message):
    """Defines what to do when simple text comes.
    - A query is formed.
    - Class Fetcher is used to fetch data from TMDB and IMDB.
    - Pretty_output function prepares the output in a nice form.
    """
    query = message.json['text']
    fetcher.get_data(query)
    out = fetcher.pretty_output()
    try:
        bot.send_message(message.chat.id, out)
    except Exception:
        bot.send_message(message.chat.id, 'Ничего не нашлось. Попробуйте еще раз!')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """Callback function that is used when a user clicks on 'Посмотри меня!'
    """
    if call.data == 'watch':
        ivi = types.InlineKeyboardButton(text='IVI', url=config.ivi_link + fetcher.query)
        okko = types.InlineKeyboardButton(text='OKKO', url=config.okko_link + fetcher.query)
        yandex = types.InlineKeyboardButton(text='Найдется все!', url=config.yandex_link + fetcher.query)

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(ivi, okko, yandex)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Попробуйте эти ресурсы:', reply_markup=keyboard)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print('Error', e)
            time.sleep(15)
