import logging
from telegram import Updater
from config import TOKEN
from random import randint, uniform, choice
from collections import defaultdict
import time
import json
import os

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARN)

logger = logging.getLogger(__name__)


delay_dict = {}
last_user_message = defaultdict(lambda: defaultdict(int))
last_chat_message = defaultdict(int)

params = {
    'freq': 4
}

random_hello_messages = {
    '{username}, Привет! Я drobot. Жму руку.': 100,
    '{username}, Я drobot. Жму руку.': 50,
}

random_responses = dict()

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
    msg = get_one_by_weight(random_hello_messages)
    bot.sendMessage(update.message.chat_id, text=msg)


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Я drobot. Жму руку.')


def response(bot, update, msg):
    author = update.message.from_user.first_name
    # text = ', '.join([author, msg])
    text = format_message(msg, username=author)
    bot.sendMessage(update.message.chat_id, text=text)


def show_me_your_genitals(bot, update):
    msg = json.dumps(random_responses, indent=4, separators=(',', ': '))
    bot.sendMessage(update.message.chat_id, text=msg)


def extend(bot, update, args):
    """
    Extend answers from chat
    """
    if len(args) > 1:
        random_responses.update({' '.join(args[:-1]): int(args[-1])})
        _save_messages()
        response(bot, update, 'Принял!')


def set_param(bot, update, args):
    if len(args) > 1:
        key, value = args[0], args[1]
        params[key] = value


def _save_messages():
    with open('new_responses.json', 'w')as f:
        msg = json.dumps(random_responses, indent=4, separators=(',', ': '))
        f.write(msg)


def _reload():
    with open('responses.json') as f:
        random_responses.update(json.load(f))

    if os.path.exists('new_responses.json'):
        with open('new_responses.json') as f:
            random_responses.update(json.load(f))


def reload_messages(bot, update):
    _reload()


def reap_something(bot, update):
    subjects = None
    try:
        subjects = update.message.text.split(' ')[:-2]
    except ValueError:
        pass

    if subjects is not None:
        txt = ' '.join(['{username}, ', 'жму', ' '.join(subjects), '!'])
        random_responses[txt] = 10
        _save_messages()
        response(bot, update, txt)


def message(bot, update):

    last_chat_message[update.message.chat_id] = time.time()

    if update.message.text.endswith('себе пожми'):
        reap_something(bot, update)
        return

    user_time = last_user_message[update.message.chat_id][update.message.from_user.id]

    if time.time() - user_time > 3600 * 24:
        last_user_message[update.message.chat_id][update.message.from_user.id] = time.time()
        response(bot, update, '{username}, рад тебя снова видеть. Жму руку!')
        return

    if update.message.chat_id not in delay_dict:
        delay_dict[update.message.chat_id] = randint(0, params['freq'])
    else:
        delay_dict[update.message.chat_id] -= 1

    if delay_dict[update.message.chat_id] == 0:
        delay_dict.pop(update.message.chat_id)
        if randint(0, 5):
            msg = get_one_by_weight(random_responses)
        else:
            # RANDOM SHAKE!
            msg = ''.join(["Жму {}".format(choice(ru_list).strip()), ', {username}!'])
        response(bot, update, msg)


def inline(bot, update):
    response(bot, update, 'а может по пивку?')


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def set_beer_alarm(bot, update):

    chat_id = update.message.chat_id

    def beer_alarm(_bot):
        if last_chat_message[chat_id] < 0:
            last_chat_message[chat_id] = 3600 * 24 * 5
            _bot.sendMessage(chat_id, text='А может по пиву сегодня?')

        last_chat_message[chat_id] -= 5

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
    dp.addTelegramCommandHandler("set_param", set_param)
    dp.addTelegramCommandHandler("show_me_your_genitals", show_me_your_genitals)

    dp.addTelegramMessageHandler(message)
    dp.addTelegramInlineHandler(inline)

    dp.addErrorHandler(error)
    updater.start_polling()
    updater.idle()
