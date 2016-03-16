import logging
from telegram import Updater
from config import TOKEN
from random import randint
from collections import defaultdict
import time

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


DELAY_DICT = {}
LAST_USER_MESSAGE = defaultdict(defaultdict(int))


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Привет! Я drobot. Жму руку.')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Я drobot. Жму руку.')


def response(bot, update, msg):
    author = update.message.from_user.first_name
    text = ', '.join([author, msg])
    bot.sendMessage(update.message.chat_id, text=text)


def message(bot, update):

    user_time = LAST_USER_MESSAGE[update.message.chat_id][update.message.from_user.id]

    if time.time() - user_time > 3600 * 24:
        LAST_USER_MESSAGE[update.message.chat_id][update.message.from_user.id] = time.time()
        response(bot, update, 'рад тебя снова видеть. Жму руку!')
        return

    if update.message.chat_id not in DELAY_DICT:
        DELAY_DICT[update.message.chat_id] = randint(0, 4)
    else:
        DELAY_DICT[update.message.chat_id] -= 1

    if DELAY_DICT[update.message.chat_id] == 0:
        DELAY_DICT.pop(update.message.chat_id)
        response(bot, update, 'жму руку!')


def inline(bot, update):
    response(bot, update, 'а может по пивку?')


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


if __name__ == '__main__':

    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("help", help)

    dp.addTelegramMessageHandler(message)
    dp.addTelegramInlineHandler(inline)

    dp.addErrorHandler(error)
    updater.start_polling()
    updater.idle()
