import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials



API_TOKEN = 'TOKEN'
bot = telebot.TeleBot(API_TOKEN)


scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("path_to_jsonServiceAccGoogle", scope)
client = gspread.authorize(creds)
sheet = client.open("News").sheet1


# Функции для парсинга заголовков RU и KZ зон
def get_ru_headlines():
    try:
        url = "https://ria.ru/world/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('a', class_='list-item__title')

        return [headline.get_text() for headline in headlines]
    except Exception as e:
        print('Ошибка в функции get_ru_headlines')
        print(e)
        print('\n')

def get_kz_headlines():
    try:
        url = "https://www.nur.kz/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('a', class_='js-article-link article-link')

        return [headline.get_text() for headline in headlines]
    except Exception as e:
        print('Ошибка в функции get_kz_headlines')
        print(e)
        print('\n')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    news_markup = types.InlineKeyboardMarkup(row_width=1)
    news_markup.add(types.InlineKeyboardButton("🇷🇺 Россия", callback_data="ru"))
    news_markup.add(types.InlineKeyboardButton("🇰🇿 Казахстан", callback_data="kz"))
    bot.send_message(message.chat.id, "Приветствую в нашем Новостном боте!\nВыбери страну, из которой хочешь получить новости:", reply_markup=news_markup)


# Тут решил немного разнообразить задачу, расширив её путём добавления двух стран на выбор
@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith('ru') or c.data.startswith('kz'))
def process_callback_country_menu(callback_query: types.CallbackQuery):
    try:
        country = str(callback_query.data)
        if country == 'ru':
            headlines = get_ru_headlines()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for headline in headlines:
                sheet.append_row([now, headline, country])

            bot.send_message(callback_query.from_user.id, "Заголовки RU новостей добавлены в таблицу.")
        else:
            headlines = get_kz_headlines()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for headline in headlines:
                sheet.append_row([now, headline, country])

            bot.send_message(callback_query.from_user.id, "Заголовки KZ новостей добавлены в таблицу.")
    except Exception as e:
        print('Ошибка в функции process_callback_country_menu')
        print(e)
        print('\n')


# Эту конструкцию выводил методом проб и ошибок на протяжении нескольких месяцев :D
if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True, timeout=999)
        except Exception as ex:
            print(ex)
            time.sleep(10)
