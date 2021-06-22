import logging
import sqlite3
import os
from pytube import YouTube
from pytube.exceptions import RegexMatchError

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
)

class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS users 
            (id INTEGER PRIMARY KEY, 
            user_id varchar, 
            chat_id varchar,
            first_name varchar, 
            last_name varchar,
            username varchar,
            language_code varchar,
            downloads int,
            lang varchar)
            """)
        self.conn.commit()
    def create(self, user_id, chat_id, first_name, last_name, username, language_code, downloads, lang):
        self.cur.execute("INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (user_id, chat_id, first_name, last_name, username, language_code, downloads, lang))
        self.conn.commit()

    def read(self):
        self.cur.execute("SELECT * FROM users")
        rows = self.cur.fetchall()
        return rows

    def update(self, user_id, chat_id, first_name, last_name, username, language_code, downloads, lang):
        self.cur.execute("UPDATE users SET chat_id = ?, first_name = ?, last_name = ?, username = ?"
                         ", language_code = ?, downloads = ?, lang = ? WHERE user_id = ?",
                         (chat_id, first_name, last_name, username, language_code, downloads, lang, user_id))
        self.conn.commit()

    def delete(self, user_id):
        self.cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database('users.db')

def start_command(update: Update, context: CallbackContext):
    start_messages = {
        'en': 'Hi! Send me a YouTube video link and I will send you the video or the audio of the video, depending '
              'on what you choose, as a document, which you can save anywhere on your device.\n\n'
              'The best way to copy YouTube video links is through the "Share this" button, which is located under every '
              'video on this video platform. Like this:',

        'ru': 'Привет! Пришли мне ссылку на YouTube видео, и я тебе вышлю это видео или аудио этого видео (в '
              'зависимости от того, что ты выберешь) в виде документа, который ты сможешь сохранить где угодно на своём '
              'устройстве.\n\nЛучше всего копировать ссылки на YouTube видео через кнопку "Поделиться", которая находится '
              'под каждым видео на этой видео-площадке. Вот, какого вида они должны быть:'
    }
    chat_id = update.message.chat_id
    user = update.message.from_user
    users = db.read()
    if str(user.id) not in [i[1] for i in users]:
        update.message.reply_text(start_messages['en'])
        db.create(str(user.id), chat_id, user.first_name, user.last_name, user.username, user.language_code,
                  0, 'en')
    else:
        for i in users:
            if i[1] == str(user.id):
                update.message.reply_text(start_messages[i[-1]])
    bot = telegram.Bot('1872481506:AAG0Wiq0kKdLjMYUnVhymuknW90Ve8-4HoY')
    file = open('screen.png', 'rb')
    bot.send_photo(chat_id=chat_id, photo=file)

def help_command(update: Update, context: CallbackContext):
    help_messages = {
        'en': 'Send me a YouTube video link and I will send you the video or the audio of the video, depending '
              'on what you choose, as a document, which you can save anywhere on your device.\n\n'
              'The best way to copy YouTube video links is through the "Share this" button, which is located under every '
              'video on this video platform.',

        'ru': 'Пришли мне ссылку на YouTube видео, и я тебе вышлю это видео или аудио формат этого видео (в '
              'зависимости от того, что ты выберешь) в виде документа, который ты сможешь сохранить где угодно на своём '
              'устройстве.\n\nЛучше всего копировать ссылки на YouTube видео через кнопку "Поделиться", которая находится '
              'под каждым видео на этой площадке.'
    }
    user_id = str(update.message.from_user.id)
    users = db.read()
    for i in users:
        if i[1] == user_id:
            update.message.reply_text(help_messages[i[-1]])

def choose_language(update: Update, context: CallbackContext):
    choose_language_messages = {
        'en': 'Choose a language:',
        'ru': 'Выберите язык:'
    }
    user_id = str(update.message.from_user.id)
    users = db.read()
    keyboard = [
        [
            InlineKeyboardButton(u'🇬🇧 ' + 'English', callback_data=f'en-{user_id}'),
            InlineKeyboardButton(u'🇷🇺 ' + 'Русский', callback_data=f'ru-{user_id}'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    for i in users:
        if i[1] == user_id:
            update.message.reply_text(choose_language_messages[i[-1]], reply_markup=reply_markup)

def stats(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    users = db.read()
    users_amount = len(users)
    downloads = 0
    lang = ''
    for i in users:
        downloads += i[-2]
        if i[1] == user_id:
            lang = i[-1]
    if lang == 'en':
        update.message.reply_text(f'Start date: 22/06/2021\n\nDownloaded: {downloads} video\n\n'
                                  f'Total users: {users_amount}')
    else:
        update.message.reply_text(f'Дата начала работы: 22/06/2021\n\nСкачано: {downloads} видео\n\n'
                                  f'Всего пользователей: {users_amount}')

def contacts(update: Update, context: CallbackContext):
    contacts_messages = {
        'en': 'Any questions or offers to this bot creator? Write me: @Anton_1mba. Or send me an email: banan3397@gmail.com',
        'ru': 'Есть вопросы или предложения к создателю бота? Пишите мне: @Anton_1mba. Или отправьте мне письмо на email: banan3397@gmail.com'
    }
    user_id = str(update.message.from_user.id)
    users = db.read()
    for i in users:
        if i[1] == user_id:
            update.message.reply_text(contacts_messages[i[-1]])

def error_pass(yt):
    while True:
        try:
            return yt.streams
        except:
            pass

def download_video(update: Update, context: CallbackContext):
    lang = ''
    choose_language_messages = {
        'en': ('Sorry, I don\'t understand the request. Please submit a YouTube video link.',
               'I can\'t download the video. Please try another link.',
               'Here what I found:'),
        'ru': ('Извини, я не могу разобрать запрос. Пожалуйста, отправь ссылку на '
               'YouTube видео.',
               'Извини, я не могу скачать это видео. Пожалуйста, попробуй другую '
               'ссылку.',
               'Вот, что я нашёл:')
    }
    user_id = str(update.message.from_user.id)
    users = db.read()
    for i in users:
        if i[1] == user_id:
            lang = i[-1]
    try:
        link = update.message.text
        yt = YouTube(link)
    except RegexMatchError:
        update.message.reply_text(choose_language_messages[lang][0])
    else:
        try:
            yt.check_availability()
        except:
            update.message.reply_text(choose_language_messages[lang][1])
        else:
            streams = error_pass(yt)
            video_streams_list = streams.filter(progressive=True)
            resolutions = []
            for i in video_streams_list:
                resolution = i.resolution
                resolution = resolution.replace('p', '')
                resolutions.append(resolution)
            resolutions = sorted(list(map(int, resolutions)), reverse=True)
            resolutions = ['VideoMP4 ' + str(i) + 'p' for i in resolutions]
            audio_stream = streams.get_audio_only()
            abr = str(audio_stream.abr)
            resolutions.append(f'AudioMP4A {abr}')
            keyboard = []
            keyboard_item = []
            for i in resolutions:
                resolution_download = i[i.find(' ') + 1:]
                keyboard_item.append(InlineKeyboardButton(i, callback_data=f'{resolution_download}-{link}-{user_id}'))
                keyboard.append(keyboard_item)
                keyboard_item = []
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(choose_language_messages[lang][2], reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    lang = ''
    button_messages = {
        'en': ('The document is larger than 50 MB, therefore I can\'t send it due to Telegram limits.',
               'Here is the video (it may take a little time to send the document):',
               'Here is the audio of the video (it may take a little time to send the document):',
               'The English language was selected.'
               ),
        'ru': ('Извини, я не могу скинуть документ из-за ограничений Telegram\'a, так как его размер '
               'превышает 50 MB.',
               'А вот и видео (отправка документа может занять немного времени):',
               'А вот и видео в аудио формате (отправка документа может занять немного времени):',
               'Выбран русский язык.'
               )
    }
    query = update.callback_query
    data = query.data
    user_id = data[data.rfind('-') + 1:]
    users = db.read()
    user = ()
    for i in users:
        if i[1] == user_id:
            user = i
            lang = i[-1]
    try:
        yt = YouTube(data[data.find('-') + 1:])
        streams = error_pass(yt)
    except:
        for i in users:
            if i[1] == user_id:
                user = i
        lang = data[:data.find('-')]
        query.answer()
        query.edit_message_text(text=button_messages[lang][3])
        db.update(user_id, user[2], user[3], user[4], user[5], user[6], user[7], lang)
    else:
        try:
            stream = streams.filter(progressive=True).get_by_resolution(resolution=data[:data.find('-')])
            filesize = stream.filesize
            title = stream.title
            title = ''.join(i for i in title if i.isalpha() or i == ' ')
            query.answer()
            if filesize / 1000000 > 50:
                query.edit_message_text(text=button_messages[lang][0])
                db.update(user_id, user[2], user[3], user[4], user[5], user[6], user[7] + 1, user[8])
                return None
            else:
                query.edit_message_text(text=button_messages[lang][1])
            stream.download(filename=title)
        except:
            stream = streams.get_audio_only()
            filesize = stream.filesize
            title = stream.title
            title = ''.join(i for i in title if i.isalpha() or i == ' ')
            query.answer()
            if filesize / 1000000 > 50:
                query.edit_message_text(text=button_messages[lang][0])
                db.update(user_id, user[2], user[3], user[4], user[5], user[6], user[7] + 1, user[8])
                return None
            else:
                query.edit_message_text(text=button_messages[lang][2])
            stream.download(filename=title)
        bot = telegram.Bot('1872481506:AAG0Wiq0kKdLjMYUnVhymuknW90Ve8-4HoY')
        chat_id = query.message.chat_id
        file = open(f'{title}.mp4', 'rb')
        bot.send_document(chat_id=chat_id, document=file)
        os.remove(f'{title}.mp4')
        db.update(user_id, user[2], user[3], user[4], user[5], user[6], user[7] + 1, user[8])

def main():
    updater = Updater('1872481506:AAG0Wiq0kKdLjMYUnVhymuknW90Ve8-4HoY')

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("lang", choose_language))
    dispatcher.add_handler(CommandHandler("stats", stats))
    dispatcher.add_handler(CommandHandler("contacts", contacts))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_video))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()