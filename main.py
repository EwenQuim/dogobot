from telegram.ext import Updater, CommandHandler
import requests
import re
import sqlite3
import datetime
from emoji import emojize
from config import token, database


# Database
con = sqlite3.connect(database)
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS commands (

    date text PRIMARY KEY,

    command text 
);""")

con.commit()

def get_url(animal="dog"):
    if animal == "dog":
        contents = requests.get('https://random.dog/woof.json').json()
        image_url = contents['url']
    else:
        contents = requests.get('http://aws.random.cat/meow').json()
        image_url = contents['file']
    return image_url

def get_image_url(animal="dog"):
    allowed_extension = ['jpg','jpeg','png']
    file_extension = ''
    while not (file_extension in allowed_extension) :
        url = get_url(animal)
        file_extension = re.search("([^.]*)$",url).group(1).lower()
    return url

def woof(update, context):
    url = get_image_url(animal="dog")
    chat_id = update.effective_chat.id 
    context.bot.send_photo(chat_id=chat_id, photo=url)  #, caption="Here's your dog !")

    conn = sqlite3.connect(database, timeout = 1000)
    with conn:
        cur = conn.cursor()
        requete = 'INSERT INTO commands (date, command) VALUES ("{}", "woof");'.format(str(datetime.datetime.now()))
        cur.execute(requete)

def meow(update, context):
    url = get_image_url(animal="cat")
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo=url)  #, caption="Here's your cat !")

    conn = sqlite3.connect(database, timeout = 1000)
    with conn:
        cur = conn.cursor()
        requete = 'INSERT INTO commands (date, command) VALUES ("{}", "meow");'.format(str(datetime.datetime.now()))
        cur.execute(requete)

def winner(update, context):
    chat_id = update.message.chat_id

    conn = sqlite3.connect(database, timeout = 1000)
    with conn:
        cur = conn.cursor()
        rq_chats = 'SELECT count(*) from commands where command = "meow";'.format(str(datetime.datetime.now()))
        rq_chiens = 'SELECT count(*) from commands where command = "woof";'.format(str(datetime.datetime.now()))
        nb_chats = cur.execute(rq_chats).fetchone()
        nb_chiens = cur.execute(rq_chiens).fetchone()
        prc_chats = int(nb_chats[0] * 100 / (nb_chats[0] + nb_chiens[0]))
        prc_chiens = 100 - prc_chats

        if prc_chats > prc_chiens :
            message = ":cat: *{0}%* - Winner ! :trophy:\n:dog: {1}%".format(prc_chats, prc_chiens)
        else:
            message = ":cat: {0}%\n:dog: *{1}%* - Winner ! :trophy:".format(prc_chats, prc_chiens)
        sent_message = emojize("Most asked animal ({} requests) :\n".format(nb_chiens[0]+nb_chats[0])+message, use_aliases=True)

        context.bot.send_message(chat_id=chat_id, text=sent_message, parse_mode='Markdown')

def main():
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('woof', woof))
    dp.add_handler(CommandHandler('meow', meow))
    dp.add_handler(CommandHandler('winner', winner))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
