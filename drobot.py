import logging
from telegram import Updater
from config import TOKEN

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Привет! Я drobot. Всем жму руку.')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Я drobot. Всем жму руку.')


def message(bot, update):
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
