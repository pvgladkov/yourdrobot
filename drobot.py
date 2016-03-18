import logging
from telegram import Updater
from config import TOKEN, params
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


class Bot(object):

    def format_message(self, msg, **kwargs):
        return msg.format(**kwargs)

    def response(self, bot, update, msg):
        author = update.message.from_user.first_name
        # text = ', '.join([author, msg])
        text = self.format_message(msg, username=author)
        bot.sendMessage(update.message.chat_id, text=text)

    def _reload(self):
        with open('responses.json') as f:
            self.random_responses.update(json.load(f))

        if os.path.exists('new_responses.json'):
            with open('new_responses.json') as f:
                self.random_responses.update(json.load(f))

    def save_messages(self):
        with open('new_responses.json', 'w')as f:
            msg = json.dumps(self.random_responses, indent=4, separators=(',', ': '), ensure_ascii=False)
            f.write(msg)


class Drobot(Bot):

    def __init__(self):
        self.random_hello_messages = {
            '{username}, Привет! Я drobot. Жму руку.': 100,
            '{username}, Я drobot. Жму руку.': 50,
        }
        self.random_responses = dict()

        self._reload()

    def reap_something(self, bot, update):
        subjects = None
        try:
            subjects = update.message.text.split(' ')[:-2]
        except ValueError:
            pass

        if subjects is not None:
            txt = ' '.join(['{username},', 'жму', ' '.join(subjects), '!'])
            self.bot.random_responses[txt] = 10
            self.bot.save_messages()
            self.bot.response(bot, update, txt)

    def message(self, bot, update):

        last_chat_message[update.message.chat_id] = time.time()

        if update.message.text.endswith('себе пожми'):
            self.reap_something(bot, update)
            return

        user_time = last_user_message[update.message.chat_id][update.message.from_user.id]

        if time.time() - user_time > 3600 * 24:
            last_user_message[update.message.chat_id][update.message.from_user.id] = time.time()
            self.bot.response(bot, update, '{username}, рад тебя снова видеть. Жму руку!')
            return

        if update.message.chat_id not in delay_dict:
            delay_dict[update.message.chat_id] = randint(0, params['freq'])
        else:
            delay_dict[update.message.chat_id] -= 1

        if delay_dict[update.message.chat_id] == 0:
            delay_dict.pop(update.message.chat_id)
            if randint(0, 5):
                msg = get_one_by_weight(self.bot.random_responses)
            else:
                # RANDOM SHAKE!
                msg = ''.join(["Жму {}".format(choice(ru_list).strip()), ', {username}!'])
            self.bot.response(bot, update, msg)


class BotApplication(object):
    def __init__(self):
        self.bot = Drobot()

    def start(self, bot, update):
        msg = get_one_by_weight(self.bot.random_hello_messages)
        bot.sendMessage(update.message.chat_id, text=msg)

    def help(self, bot, update):
        bot.sendMessage(update.message.chat_id, text='Я drobot. Жму руку.')

    def message(self, bot, update):
        self.bot.message(bot, update)

    def extend(self, bot, update, args):
        """
        Extend answers from chat
        """
        if len(args) > 1:
            self.bot.random_responses.update({' '.join(args[:-1]): int(args[-1])})
            self.bot.save_messages()
            self.bot.response(bot, update, 'Принял!')

    def set_param(self, bot, update, args):
        if len(args) > 1:
            try:
                key, value = args[0], int(args[1])
                params[key] = value
            except ValueError:
                pass


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

    bot_app = BotApplication()

    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.addTelegramCommandHandler("start", bot_app.start)
    dp.addTelegramCommandHandler("help", bot_app.help)
    dp.addTelegramCommandHandler("set_beer_alarm", set_beer_alarm)
    dp.addTelegramCommandHandler("extend", bot_app.extend)
    dp.addTelegramCommandHandler("set_param", bot_app.set_param)

    dp.addTelegramMessageHandler(bot_app.message)

    dp.addErrorHandler(error)
    updater.start_polling()
    updater.idle()
