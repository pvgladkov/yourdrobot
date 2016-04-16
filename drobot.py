import logging
from telegram import Updater
from config import TOKEN, params
from random import randint, uniform, choice
from collections import defaultdict
from filedict import FileDict
import time
import json
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARN)

logger = logging.getLogger(__name__)


delay_dict = {}
last_chat_message = defaultdict(int)
ru_list = open('zdf.txt').readlines()
humiliation_messages = {
    'Хаха, {username} лох': 1,
    'Мамку свою админь, {username}': 1,
    'Хочешь стать админом, {username}?': 2,
}


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


def admin(method):
    def humiliation(self, bot, update, args):
        msg = get_one_by_weight(humiliation_messages)
        self.bot.response(bot, update, msg=msg)

    def wrapper(self, bot, update, args):
        if update.message.from_user.id in params['admins']:
            return method(self, bot, update, args)
        return humiliation(self, bot, update, args)
    return wrapper


class Bot(object):

    def __init__(self):
        self.last_user_message = defaultdict(lambda: defaultdict(int))
        self.prefix = self.__class__.__name__
        self.base_file = 'responses/{}_base.json'.format(self.prefix)
        self.dynamic_file = 'responses/{}_dynamic.json'.format(self.prefix)
        self.users_file = 'responses/{}_users.json'.format(self.prefix)
        self.last_msgs_file = 'responses/{}_last_msgs.json'.format(self.prefix)
        self.names = defaultdict()

        if os.path.exists(self.users_file):
            with open(self.users_file) as f:
                self.names.update(json.load(f))

        if os.path.exists(self.last_msgs_file):
            with open(self.last_msgs_file) as f:
                self.last_user_message = json.load(f)

    def _save_json(self, name, obj):
        with open(name, 'w')as f:
            msg = json.dumps(
                obj,
                indent=4,
                separators=(',', ': '),
                ensure_ascii=False)
            f.write(msg)

    def get_author(self, user):
        name = self.names.get(str(user.id), None)
        if name is None:
            name = user.first_name
        return name

    def format_message(self, msg, **kwargs):
        return msg.format(**kwargs)

    def response(self, bot, update, msg):
        author = self.get_author(update.message.from_user)
        text = self.format_message(msg, username=author)
        bot.sendMessage(update.message.chat_id, text=text)

    def _reload(self):
        with open(self.base_file) as f:
            self.random_responses.update(json.load(f))

        if os.path.exists(self.dynamic_file):
            with open(self.dynamic_file) as f:
                self.random_responses.update(json.load(f))

    def save_messages(self):
        self._save_json(self.dynamic_file, self.random_responses)

    def message(self, bot, update):
        pass

    def conversion(self, bot, update):
        msg = update.message.text
        self.response(bot, update, msg)

    def _save_names(self):
        self._save_json(self.users_file, self.names)

    def _save_user_messeages(self):
        self._save_json(self.last_msgs_file, self.last_user_message)


class Drobot(Bot):

    def __init__(self):
        super(Drobot, self).__init__()
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
            txt = ''.join(['{username}, ', 'жму ', ' '.join(subjects), '!'])
            self.random_responses[txt] = 10
            self.save_messages()
            self.response(bot, update, txt)

    def message(self, bot, update):

        last_chat_message[update.message.chat_id] = time.time()

        if update.message.text.endswith('себе пожми'):
            self.reap_something(bot, update)
            return

        user_time = self.last_user_message.get(str(update.message.from_user.id), 0)

        if time.time() - user_time > 3600 * 24:
            self.last_user_message[str(update.message.from_user.id)] = time.time()
            self.response(bot, update, '{username}, рад тебя снова видеть. Жму руку!')
            self._save_user_messeages()
            return

        if update.message.chat_id not in delay_dict:
            delay_dict[update.message.chat_id] = randint(0, params['freq'])
        else:
            delay_dict[update.message.chat_id] -= 1

        if delay_dict[update.message.chat_id] == 0:
            delay_dict.pop(update.message.chat_id)
            if randint(0, 5):
                msg = get_one_by_weight(self.random_responses)
            else:
                # RANDOM SHAKE!
                msg = ''.join(["Жму {}".format(choice(ru_list).strip()), ', {username}!'])
            self.response(bot, update, msg)

    def conversion(self, bot, update):
        pass

    def rename(self, bot, update):
        name = ' '.join(update.message.text.split(' ')[3:])
        uid = str(update.message.from_user.id)
        self.names[uid] = name
        msg = "Хорошо, {}".format(name)
        self.response(bot, update, msg)
        self._save_names()

    def rombika(self, bot, update):
        phrases = {
            'Все в порядке, завтра запускаемся, {username}': 10,
            '{username}, все в порядке, завтра запускаемся!': 10,
            'Все в порядке, завтра запускаемся!': 10,
        }
        msg = get_one_by_weight(phrases)
        self.response(bot, update, msg)

    def drobot(self, bot, update):
        phrases = {
            'Я тут, слушаю тебя': 10,
            'Я тут, слушаю тебя, {username}': 10,
            '{username}, слушаю тебя': 10,
        }
        msg = get_one_by_weight(phrases)
        self.response(bot, update, msg)

    def router(self, bot, update):
        msg = update.message.text
        if msg.lower().find('дробот') > -1:
            self.drobot(bot, update)
            return
        if msg.lower().find('ромбик') > -1:
            self.rombika(bot, update)
            return
        if msg.startswith('@yourdrobot'):
            msg = msg[12:]
            if msg.startswith('зови меня'):
                self.rename(bot, update)
            else:
                msg = get_one_by_weight(self.random_responses)
                self.response(bot, update, msg)
        else:
            self.message(bot, update)


class BotApplication(object):

    bot = 'Drobot'
    chat_id = 0

    def __init__(self, dp):
        self.bot = Drobot()

        dp.addTelegramCommandHandler("admin", self.lol_admin)
        dp.addTelegramCommandHandler("start", self.start)
        dp.addTelegramCommandHandler("help", self.help)
        dp.addTelegramCommandHandler("extend", self.extend)
        dp.addTelegramCommandHandler("set_param", self.set_param)
        dp.addTelegramCommandHandler("set_active_chat_id", self.set_active_chat_id)
        dp.addTelegramCommandHandler("say", self.say)
        dp.addTelegramCommandHandler("myid", self.myid)

        dp.addTelegramMessageHandler(self.bot.router)
        # dp.addTelegramRegexHandler('[^@yourdrobot].*', self.bot.message)
        # dp.addTelegramRegexHandler('@yourdrobot зови меня .*', self.bot.rename)
        # dp.addTelegramRegexHandler('@yourdrobot.*', self.conversion)

    @admin
    def lol_admin(self, bot, update, args):
        msg = 'Инструкции отправлены в личку, {username}'
        self.bot.response(bot, update, msg)

    @admin
    def start(self, bot, update, args):
        msg = get_one_by_weight(self.bot.random_hello_messages)
        msg = "{} chat_id: {}".format(msg, update.message.chat_id)
        self.bot.response(bot, update, msg)

    def help(self, bot, update, args):
        bot.sendMessage(update.message.chat_id, text='Я drobot. Жму руку.')

    @admin
    def extend(self, bot, update, args):
        """
        Extend answers from chat
        """
        if len(args) > 1:
            self.bot.random_responses.update({' '.join(args[:-1]): int(args[-1])})
            self.bot.save_messages()
            self.bot.response(bot, update, 'Принял!')

    @admin
    def set_active_chat_id(self, bot, update, args):
        msg = "Неверный формат"
        try:
            self.chat_id = int(update.message.chat_id)
            msg = "Чат обновлен"
        except:
            pass
        bot.sendMessage(self.chat_id, text=msg)

    @admin
    def say(self, bot, update, args):
        msg = update.message.text
        if self.chat_id:
            bot.sendMessage(self.chat_id, text=msg[4:])

    def set_param(self, bot, update, args):
        if len(args) > 1:
            try:
                key, value = args[0], int(args[1])
                params[key] = value
            except ValueError:
                pass

    def myid(self, bot, update, args):
        uid = update.message.from_user.id
        self.bot.response(bot, update, 'Ты {}, username'.format(uid))

    def conversion(self, bot, update):
        self.bot.conversion(bot, update)


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

    updater = Updater(TOKEN)
    dp = updater.dispatcher
    bot_app = BotApplication(dp)

    dp.addTelegramCommandHandler("set_beer_alarm", set_beer_alarm)
    dp.addErrorHandler(error)
    updater.start_polling()
    updater.idle()
