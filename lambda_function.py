import logging

from PIL import Image
import requests
import telebot
import json
import os
import io

from cutter import cut_to_parts

API_TOKEN = os.environ['TELEGRAM_TOKEN']

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN, threaded=False)


def send_pillow(chat_id, im, as_type='photo', filename='file'):
    buf = io.BytesIO()
    im.save(buf, format="jpeg")
    buf = io.BytesIO(buf.getvalue())

    if as_type == 'photo':
        bot.send_photo(chat_id, buf)
        print(f'sendPhoto')
    elif as_type == 'document':
        buf.name = filename
        bot.send_document(chat_id, buf)
        print(f'sendDocument')


def process_event(event):
    # Get telegram webhook json from event
    request_body_dict = json.loads(event['body'])
    # Parse updates from json
    update = telebot.types.Update.de_json(request_body_dict)
    # Run handlers and etc for updates
    bot.process_new_updates([update])


def lambda_handler(event, context):
    # Process event from aws and respond
    process_event(event)
    return {
        'statusCode': 200
    }


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! Send me a panoram or another type of wide photo")


# Handle photos and documents with photos other messages
@bot.message_handler(func=lambda message: message.document.mime_type in ['image/jpeg', 'image/png'],
                     content_types=['document'])
@bot.message_handler(func=lambda message: True, content_types=['photo'])
def process_image(message):
    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
    elif message.document:
        file_info = bot.get_file(message.document.file_id)
    else:
        return

    if file_info.file_size > 10000000:
        print('File is too big')
        bot.reply_to(message, "File is too big")
        return

    # download image
    downloaded_file = bot.download_file(file_info.file_path)

    # process image
    img = Image.open(io.BytesIO(downloaded_file))
    p, full, ok = cut_to_parts(img)

    if not ok:
        print('Error, wrong image')
        bot.reply_to(message, "I can't cut this image :(")
        return

    chat_id = message.chat.id

    # send images back
    for part in p:
        send_pillow(chat_id, part)
    send_pillow(chat_id, full)

    if message.document:
        for i in range(len(p)):
            send_pillow(chat_id, p[i], 'document', f'{i}.jpg')
        send_pillow(chat_id, full, 'document', 'full.jpg')


@bot.message_handler()
def unknown_message(message):
    bot.reply_to(message, 'Send me a panorama and i will cut it to images for instagram')
