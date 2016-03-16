import logging
from telegram import Updater
from config import TOKEN
from random import randint

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


DELAY_DICT = {}


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Привет! Я drobot. Жму руку.')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Я drobot. Жму руку.')


def message(bot, update):

    if update.message.chat_id not in DELAY_DICT:
        DELAY_DICT[update.message.chat_id] = randint(0, 10)
    else:
        DELAY_DICT[update.message.chat_id] -= 1

    if DELAY_DICT[update.message.chat_id] == 0:
        DELAY_DICT.pop(update.message.chat_id)
        author = update.message.from_user.first_name
        text = ', '.join([author, 'жму руку!'])
        bot.sendMessage(update.message.chat_id, text=text)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


if __name__ == '__main__':

    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("help", help)

    dp.addTelegramMessageHandler(message)

    dp.addErrorHandler(error)
    updater.start_polling()
    updater.idle()
