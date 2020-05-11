# -*- coding: utf-8 -*-

import time
import apiclient
import httplib2
import telebot
import requests
from oauth2client.service_account import ServiceAccountCredentials

BOT_TOKEN = '#YOUR_TELEGRAM_BOT_TOKEN#'
CREDENTIALS_FILE = 'creds.json'
SPREADSHEETS_ID = '#YOUR_SPREADSHEETS_IDENTIFIER#'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
# YOUR CHAT ID
CHAT_ID = 123456789
# YOUR ORDER FIELD
RANGE_EXAMPLE = 'A:F'


def authorization_in_google():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES)
    http_auth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=http_auth)
    return service


def read_sheets(service):
    massage = service.spreadsheets().values().get(spreadsheetId=SPREADSHEETS_ID,
                                                  range=RANGE_EXAMPLE,
                                                  majorDimension='ROWS'
                                                  ).execute()
    return massage


def get_orders_information(service):
    text = read_sheets(service)['values']
    return text


def send_new_orders(message, chat_id, chat_bot):
    chat_bot.send_message(chat_id=chat_id, text=message)


key = authorization_in_google()
orders = get_orders_information(service=key)
print('All current orders:', orders[1:])

bot = telebot.TeleBot(BOT_TOKEN)

try:
    while True:
        current_orders = get_orders_information(service=key)
        new_orders = [items for items in current_orders if items not in orders]
        if new_orders:
            print('New orders appear:', new_orders)
            try:
                send_new_orders(message=str(new_orders), chat_id=CHAT_ID, chat_bot=bot)
            except requests.exceptions.SSLError:
                print('Except error with SSL. Check your connection to telegram.api. Maybe you are blocked.')
                break
            orders = current_orders
        time.sleep(20)
except httplib2.ServerNotFoundError:
    print('Server not found. Check your connection.')
