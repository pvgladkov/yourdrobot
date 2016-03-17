import logging
from telegram import Updater
from config import TOKEN
from random import randint, uniform, choice
from collections import defaultdict
import time
import json

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


DELAY_DICT = {}
LAST_USER_MESSAGE = defaultdict(lambda: defaultdict(int))
LAST_CHAT_MESSAGE = defaultdict(int)

RANDOM_MESSAGE = {
    '{username}, Привет! Я drobot. Жму руку.': 100,
    '{username}, Я drobot. Жму руку.': 50,
}

RANDOM_RESPONSE = dict()

ru_list = open('zdf.txt').readlines()


def get_one_by_weight(data):
    """
    Возвращает одно из значений с учетом веса.
    где data имеет вид: {"1":20,"2":10}
    ключ - возвращаемое значение,
    значение - вес ключа.
    """
    total = sum(data.values())
    n = uniform(0, total)
    for key in sorted(data.keys()):
        item = key
        if n < data[key]:
            break
        n -= data[key]
    return item


def format_message(msg, **kwargs):
    return msg.format(**kwargs)


def start(bot, update):
    msg = get_one_by_weight(RANDOM_MESSAGE)
    bot.sendMessage(update.message.chat_id, text=msg)


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Я drobot. Жму руку.')


def response(bot, update, msg):
    author = update.message.from_user.first_name
    # text = ', '.join([author, msg])
    text = format_message(msg, username=author)
    bot.sendMessage(update.message.chat_id, text=text)


def show_me_your_genitals(bot, update):
    msg = json.dumps(RANDOM_MESSAGE, indent=4, separators=(',', ': '))
    bot.sendMessage(update.message.chat_id, text=msg)


def extend(bot, update, msg):
    """
    Extend answers from chat
    """
    msg = json.loads(msg)
    RANDOM_MESSAGE.update(msg)
    with open('responses.json', 'w')as f:
        msg = json.dumps(RANDOM_MESSAGE, indent=4, separators=(',', ': '))
        f.write(msg)


def _reload():
    with open('responses.json') as f:
        RANDOM_MESSAGE.update(json.loads(f.readall()))


def reload_messages(bot, update):
    _reload()


def reap_something(bot, update):
    subject = None
    try:
        subject, _, _ = update.message.text.split(' ')
    except ValueError:
        pass

    if subject is not None:
        txt = ' '.join(['{username}, ', 'жму', subject, '!'])
        RANDOM_RESPONSE[txt] = 10
        with open('responses.json') as f:
            json.dump(RANDOM_RESPONSE, f)
        response(bot, update, txt)


def message(bot, update):

    LAST_CHAT_MESSAGE[update.message.chat_id] = time.time()

    if update.message.text.endswith('себе пожми'):
        reap_something(bot, update)
        return

    user_time = LAST_USER_MESSAGE[update.message.chat_id][update.message.from_user.id]

    if time.time() - user_time > 3600 * 24:
        LAST_USER_MESSAGE[update.message.chat_id][update.message.from_user.id] = time.time()
        response(bot, update, '{username}, рад тебя снова видеть. Жму руку!')
        return

    if update.message.chat_id not in DELAY_DICT:
        DELAY_DICT[update.message.chat_id] = randint(0, 4)
    else:
        DELAY_DICT[update.message.chat_id] -= 1

    if DELAY_DICT[update.message.chat_id] == 0:
        DELAY_DICT.pop(update.message.chat_id)
        if randint(0, 5):
            msg = get_one_by_weight(RANDOM_RESPONSE)
        else:
            # RANDOM SHAKE!
            msg = ''.join(["Жму {}".format(choice(ru_list)), ', {username}!'])
        response(bot, update, msg)


def inline(bot, update):
    response(bot, update, 'а может по пивку?')


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def set_beer_alarm(bot, update):

    chat_id = update.message.chat_id

    def beer_alarm(_bot):
        if LAST_CHAT_MESSAGE[chat_id] < 0:
            LAST_CHAT_MESSAGE[chat_id] = 3600 * 24 * 5
            _bot.sendMessage(chat_id, text='А может по пиву сегодня?')

        LAST_CHAT_MESSAGE[chat_id] -= 5

    updater.job_queue.put(beer_alarm, 5, repeat=True)

if __name__ == '__main__':

    _reload()

    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("help", help)
    dp.addTelegramCommandHandler("reload", reload_messages)
    dp.addTelegramCommandHandler("set_beer_alarm", set_beer_alarm)
    dp.addTelegramCommandHandler("extend", extend)
    dp.addTelegramCommandHandler("show_me_your_genitals", show_me_your_genitals)

    dp.addTelegramMessageHandler(message)
    dp.addTelegramInlineHandler(inline)

    dp.addErrorHandler(error)
    updater.start_polling()
    updater.idle()
