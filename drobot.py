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
LAST_USER_MESSAGE = defaultdict(lambda: defaultdict(int))

RANDOM_MESSAGE = {
    'Привет! Я drobot. Жму руку.': 100,
    'Я drobot. Жму руку.': 50,
}
RANDOM_RESPONSE = {
    'рад тебя снова видеть. Жму руку!': 50,
    'жму руку!': 50,
    'Жму Анус!': 10,
    'Жму кальмара!':10,
    'два кальмара этому господину!':5,
}

def get_one_by_weight(data):
    """
    Возвращает одно из значений с учетом веса.
    где data имеет вид: {"1":20,"2":10}
    ключ - возвращаемое значение,
    значение - вес ключа.
    """
    total = sum(data.values())
    n = random.uniform(0, total)
    for key in sorted(data.keys()):
        item = key
        if n < data[key]:
            break
        n -= data[key]
    return item

def start(bot, update):
    msg = get_one_by_weight(RANDOM_MESSAGE)
    bot.sendMessage(update.message.chat_id, text=msg)


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Я drobot. Жму руку.')


def response(bot, update, msg):
    author = update.message.from_user.first_name
    text = ', '.join([author, msg])
    bot.sendMessage(update.message.chat_id, text=text)


def message(bot, update):

    user_time = LAST_USER_MESSAGE[update.message.chat_id][update.message.from_user.id]

    logging.info(str(user_time))

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
        msg = get_one_by_weight(RANDOM_RESPONSE)
        response(bot, update, msg)


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
