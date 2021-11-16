import logging
import os
import requests

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))

# Hide the telegram bot token
TOKEN = os.environ["TOKEN"]

# testing other commands
GENDER, PHOTO, LOCATION, BIO = range(4)


def fake_start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [['Boy', 'Girl', 'Other']]

    update.message.reply_text(
        'Hi! My name is Professor Bot. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'Are you a boy or a girl?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Boy or Girl?'
        ),
    )

    return GENDER


def gender(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'I see! Please send me a photo of yourself, '
        'so I know what you look like, or send /skip if you don\'t want to.',
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


def photo(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Now, send me your location please, or send /skip if you don\'t want to.'
    )

    return LOCATION


def skip_photo(update: Update, context: CallbackContext) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'I bet you look great! Now, send me your location please, or send /skip.'
    )

    return LOCATION


def location(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text(
        'Maybe I can visit you sometime! At last, tell me something about yourself.'
    )

    return BIO


def skip_location(update: Update, context: CallbackContext) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text(
        'You seem a bit paranoid! At last, tell me something about yourself.'
    )

    return BIO


def bio(update: Update, context: CallbackContext) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def get_last_post():
    """Gets the info about the last post"""
    url = "https://instagram40.p.rapidapi.com/account-feed"

    querystring = {"username":"student_council_nis_kst"}

    headers = {
        'x-rapidapi-host': "instagram40.p.rapidapi.com",
        'x-rapidapi-key': "75a080a24bmsh79caf9b2328fd8dp167288jsn32cf0cdfd80d"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    # last_post = response.json()[0]
    for i in range(12):
        if response.json()[i]['node']['shortcode']=="CWQMSSfgEAl":
            last_post = response.json()[i]

    text = last_post['node']['edge_media_to_caption']['edges'][0]['node']['text']
    shortcode = last_post['node']["shortcode"]

    return text + "\n\nСсылка на инстаграм пост: https://www.instagram.com/p/" + shortcode


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Привет! Я тут чтобы помочь. Отправь /help для справки по боту.')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
    """
    Привет еще раз! У меня есть несколько команд:
/help - это сообщение которое вы сейчас читаете, тут справка по командам и функциям бота
/link – если вы хотите получить ссылку на полезные материалы по подготовке к экзаменам IELTS, SAT, МЭСК. Материалы будут регулярно обновляться 
/private – вызвав эту команду, вы сможете анонимно поделиться какой-либо проблемой с волонтерами и психологами, которые готовы помочь и ответить вам с помощью этого бота
/suggestion - если у вас есть предложения по улучшению нашей школы, мы будем рады вас выслушать
/complaint - если вас что-то не устраивает в нашей школе, вызовите эту команду
/question - если у вас есть вопрос к Student Council, задавайте сюда
/bot_feedback - любые предложение/жалобы/вопросы/благодарности по боту
Последние 5 команд должны быть в формате /(команда) текст. Например, /suggestion хотелось бы провести киновечер.
В других случаях бот отправляет ваши сообщения в группу NIS Kostanay анонимно, где его видят все присутствующие в этой беседе. Это можно использовать в различных целях, например, признаться кому-либо в своих чувствах, либо просто поделиться чем-нибудь, не раскрывая свою личность. 
Просьба воздержаться от нецензурной лексики, рекламы, флуда и спама. Подобные сообщения будут немедленно удаляться. Заранее благодарим!
    """
    )


def suggestion(update, context):
    """Handles the /suggestion command"""
    context.bot.send_message(chat_id=-1001096346677, text=str(update.message.text)+"\n#suggestion")


def complaint(update, context):
    """Handles the /complaint command"""
    context.bot.send_message(chat_id=-1001096346677, text=str(update.message.text)+"\n#complaint")


def question(update, context):
    """Handles the /question command"""
    context.bot.send_message(chat_id=-1001096346677, text=str(update.message.text)+"\n#question")


def bot_feedback(update, context):
    """Handles the /bot_feedback command"""
    context.bot.send_message(chat_id=-1001096346677, text=str(update.message.text)+"\n#bot_feedback")


def private(update, context):
    """Handles the /private command"""
    context.bot.send_message(chat_id=-1001096346677, text=str(update.message.text)+"\n#private")


def ig(update, context):
    """Send the last instagram post when the command /ig is issued"""
    update.message.reply_text(get_last_post())


def redirect(update, context):
    """Redirect the user message."""
    context.bot.send_message(chat_id=-1001248260165, text=update.message.text)


def post(update, context):
    """Redirect the user message."""
    context.bot.send_message(chat_id=-1001248260165)


def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # test
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('fake_start', fake_start)],
        states={
            GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],
            PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
            LOCATION: [
                MessageHandler(Filters.location, location),
                CommandHandler('skip', skip_location),
            ],
            BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("ig", ig))
    dp.add_handler(CommandHandler('suggestion', suggestion))
    dp.add_handler(CommandHandler('complaint', complaint))
    dp.add_handler(CommandHandler('question', question))
    dp.add_handler(CommandHandler('bot_feedback', bot_feedback))
    dp.add_handler(CommandHandler('private', private))
    

    # on noncommand i.e message - redirect the message on Telegram
    dp.add_handler(MessageHandler(Filters.chat(514347981), post))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.chat([-1001248260165, -1001096346677, 514347981])), redirect))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url="https://niskostanaycounsellingbot.herokuapp.com/" + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()