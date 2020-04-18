from telegram.ext import Updater
import requests
from bs4 import BeautifulSoup
import pandas as pd

# set up the logging module, so you will know when (and why) things don't work as expected
import logging
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)

TOKEN = '1299635754:AAG0RWiaJgKlaFbnHeeeTgTocce7VymITGk'
updater = Updater(token = TOKEN, use_context = True)

# Now, you can define a function that should process a specific type of update
def start(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Hey there, Wanna know about Stock Market and stuff?")


from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def get_stock_prices(update, context):
    # taking country input from user
    country = input("Tell me the country name: ")

    # load csv and get dataframe
    df = pd.read_csv('stock_indices.csv')

    # making all country names capital so that comparison btw country variable and country column is insensitive
    df['Country'] = df['Country'].str.upper()
    df['Indices'] = df['Indices'].str.upper()
    df.drop(columns = ['Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7'], inplace = True)

    # check which country user has entered and get its indice
    indice = df[df['Country'].str.contains(country.upper())].reset_index()
    indice.drop(columns = ['index'], inplace = True)

    # loop if one country has more than one indices like US
    for index in indice.iterrows():
        # webpage having all countries stock indices
        url = index[1]['URL']
        stock = index[1]['Indices']
        name = index[1]['Country']

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # getting stock price
        price = soup.find_all('div', {'class' : 'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text

        # getting currency string
        c = soup.find_all('div', {'class' : 'C($tertiaryColor) Fz(12px)'})[0].find('span').text

        # getting required string for currency by splliting by dot(.)
        currency = c.rsplit('.')[1]
        # removing a left spaces from string
        currency = currency.lstrip()

        # final printing format for user
        print('COUNTRY : ' + name + '\n' + stock + ' --> ' + price + '\n' + currency.upper())


stock_handler = CommandHandler('stock', get_stock_prices)
dispatcher.add_handler(stock_handler)


updater.start_polling()
