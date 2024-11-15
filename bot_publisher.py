import time
import traceback

import asyncio
import configparser
from aiogram import Bot
from aiogram.utils import exceptions
import schedule
import openai
import random
import pandas as pd
from datetime import datetime
import os
import numpy as np

from res import openai_api_requests, utils

config = configparser.ConfigParser()
config.read('res/config_true.ini', encoding='utf-8')
openai.api_key = config['openai']['api']
font_s = eval(config['parameters']['font_size'])

# TODO add chatGPT grammar check
# TODO add chatGPT translation to english for dalle
# TODO train additional memes on a custom model

async def send_meme_image(bot_token, channel_id, image_path, data_path, text, fontsize, type_='random', post=True):

    """""
    type_ - random, js, wolf
    """""

    # Data
    df_init = pd.read_csv(os.path.join(data_path, 'history_data.csv'), sep=';', encoding='cp1251')
    id_loc = df_init['id'].max()
    if id_loc is np.nan:
        id_loc = 0
    else:
        id_loc = id_loc + 1
    cr_dt_loc = datetime.today()

    # Call functions to generate a new meme image
    if type_ == 'random':

        meme_text = openai_api_requests.generate_meme_text(text)
        print(f"Meme text: {meme_text}")

        meme_text_trns = openai_api_requests.generate_meme_text('Перевди текст на английский:' + meme_text.split('|')[0])
        print(f"Meme text: {meme_text_trns}")

        meme_url = openai_api_requests.generate_meme_image_openai(meme_text_trns)
        print(f"Meme URL: {meme_url}")

        meme_text = meme_text.split('|')[-1]

        meme_text_img = None

    elif type_ == 'js':

        print('It`s Jason Statham time!')

        meme_text = openai_api_requests.generate_meme_text(text)
        print(f"Meme text: {meme_text}")

        rand_js = random.randint(1, 4)
        if rand_js == 1:
            meme_text_img = 'thoughtful jason statham'
        elif rand_js == 2:
            meme_text_img = 'happy jason statham'
        elif rand_js == 3:
            meme_text_img = 'jason statham with a gun'
        else:
            meme_text_img = 'serious jason statham'
        meme_url = openai_api_requests.generate_meme_image_openai(meme_text_img)
        print(f"Meme URL: {meme_url}")

    elif type_ == 'wolf':

        print('It`s AUF time!')

        meme_text = openai_api_requests.generate_meme_text(text)
        print(f"Meme text: {meme_text}")

        meme_text_trns = openai_api_requests.generate_meme_text('Перевди текст на английский:' + meme_text)
        print(f"Meme text: {meme_text_trns}")

        meme_url = openai_api_requests.generate_meme_image_openai(meme_text_trns)
        print(f"Meme URL: {meme_url}")

        meme_text_img = None

    else:

        meme_text = openai_api_requests.generate_meme_text(text)
        print(f"Meme text: {meme_text}")

        meme_text_trns = openai_api_requests.generate_meme_text('Перевди текст на английский:' + meme_text)
        print(f"Meme text: {meme_text_trns}")

        meme_url = openai_api_requests.generate_meme_image_openai(meme_text_trns)
        print(f"Meme URL: {meme_url}")

        meme_text_img = None

    # If why - then split the text into two parts and place them at the top and bottom respectively
    if 'почему' in meme_text.split(' ')[0].lower() and len(meme_text.split('?')) == 2:
        utils.download_image_and_two_texts(meme_url, meme_text.split('?')[0] + '?', meme_text.split('?')[1], image_path, font_s, data_path, 0)
    else:
        utils.download_image_and_add_text(meme_url, meme_text, image_path, fontsize, data_path, id_=id_loc)
    print(f"Image saved as {image_path}")

    # Saving log
    df_loc = pd.DataFrame({'id': [id_loc],
                           'creation_date': [cr_dt_loc],
                           'text': [meme_text],
                           'image_url': [meme_url],
                           'meme_text_img': [meme_text_img]})
    df_out = pd.concat([df_init, df_loc], axis=0)
    df_out.to_csv(os.path.join(data_path, 'history_data.csv'), sep=';', encoding='cp1251', index=False)

    # Posting
    if post:
        # Launch bot
        bot = Bot(token=bot_token)

        try:
            with open(image_path, 'rb') as image_file:
                await bot.send_photo(chat_id=channel_id, photo=image_file)

        except exceptions.ChatNotFound:
            print("Telegram channel not found. Please check your channel ID.")
        except exceptions.BadRequest:
            print("Sending the image failed. Please check your bot token and channel ID.")
        finally:
            await bot.close()
    else:
        print('post parameter is False. The message would not be sent.')

def run_loop(prompt, fontsize, type_='random', post=True):
    try:
        image_path = "temp/meme_image.jpg"  # The path to the generated meme image
        data_path = "data"

        loop = asyncio.get_event_loop()
        loop.run_until_complete(send_meme_image(BOT_TOKEN, CHANNEL_ID, image_path, data_path, prompt, fontsize, type_=type_, post=post))

        print('Done')
    except:
        traceback.print_exc()
        time.sleep(30)

if __name__ == "__main__":

    try:
        config = configparser.ConfigParser()
        config.read('res/config_true.ini', encoding='utf-8')

        BOT_TOKEN = config['telegram']['bot_token']
        CHANNEL_ID = config['telegram']['channel_id']

        prompt = config['parameters']['prompt']
        prompt2 = config['parameters']['prompt2']
        prompt3 = config['parameters']['prompt3']
        font_size = eval(config['parameters']['font_size'])
    except:
        traceback.print_exc()
        time.sleep(30)

    # run_loop(prompt3, font_size, type_='wolf', post=False)

    print('Bot polling')

    # schedule.every().day.at('11:00').do(run_loop, prompt, font_size, type_='js')
    schedule.every().day.at('11:00').do(run_loop, prompt2, font_size, type_='random')
    schedule.every().day.at('14:00').do(run_loop, prompt2, font_size, type_='random')
    schedule.every().day.at('17:00').do(run_loop, prompt3, font_size, type_='wolf')
    schedule.every().day.at('20:00').do(run_loop, prompt3, font_size, type_='wolf')

    while True:
        schedule.run_pending()
        time.sleep(5)



