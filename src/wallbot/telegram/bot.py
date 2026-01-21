import logging
import time

import telebot

from src.wallbot.config.settings import TOKEN


def create_bot():
    logging.info("Creating bot")
    return telebot.TeleBot(TOKEN)


def start_bot(bot, times):
    try:
        time.sleep(times)
        logging.info("Connecting to Telegram")
        bot.polling(none_stop=True, timeout=3000)
    except Exception as e:
        logging.error(
            "An error occurred with the Telegram call. Retrying connection", e)
        print("An error occurred with the Telegram call. Retrying connection")
        if times > 16:
            times = 16

        start_bot(bot, times * 2)
