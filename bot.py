from telegram.ext import Updater, CommandHandler
import requests
from bs4 import BeautifulSoup
import pandas as pd

'''
# set up the logging module, so you will know when (and why) things don't work as expected
import logging
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)

updater = Updater(token = TOKEN, use_context = True)
'''

# Now, you can define a function that should process a specific type of update

def index_price(country):
    # load csv and get dataframe
    df = pd.read_csv('stock_indices.csv')

    # check which country user has entered and get its indice
    indice = df[df['Country'].str.contains(country.upper())].reset_index()
    indice.drop(columns = ['index'], inplace = True)

    # if indice is empty that means the given country is not in the database
    if(indice.empty):
        return " "

    # initializing indexes variable
    indexes = ""

    # loop if one country has more than one indices like US
    for index in indice.iterrows():
        # webpage having all countries stock indices
        url = index[1]['URL']
        stock = index[1]['Indices']

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
        # removing extra words
        currency = currency.replace("Currency in ", "")

        indexes += "Currently the " + str(stock) + " stands at " + str(price) + " " + str(currency) + "\n"

    return indexes


def start(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Hey there, Wanna know about Stock Market and stuff?")

def get_country_list(update, context):
        df = pd.read_csv('stock_indices.csv')
        countries = "Here is your list:\n"
        # really smart move
        for c in df['Country']:
            countries += c + "\n"
        context.bot.send_message(chat_id = update.effective_chat.id, text = countries)

def get_stock_prices(update, context):
    # taking country input from user
    # country = input("Tell me the country name: ")
    if context.args == []:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Type in the country name as the KeyWord along with the index command')
        return
    #if len(context.args) != 1:
    #    context.bot.send_message(chat_id=update.effective_chat.id, text='Only one argument allowed')
    #    return
    context.bot.send_message(chat_id=update.effective_chat.id, text= "Just a sec! Finding related info!")
    country = " ".join(context.args)
    stock_indices = index_price(country)
    if(stock_indices == " "):
        context.bot.send_message(chat_id=update.effective_chat.id, text= "Sorry, I don't have data for this. Take a look at the country list by command /country.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text = stock_indices)




def main():
    TOKEN = "1299635754:AAG0RWiaJgKlaFbnHeeeTgTocce7VymITGk"
    #PORT = int(os.environ.get('PORT', '8443'))
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dp.add_handler(start_handler)
    stock_handler = CommandHandler('index', get_stock_prices)
    dp.add_handler(stock_handler)
    country_handler = CommandHandler('country', get_country_list)
    dp.add_handler(country_handler)
    updater.start_polling()
    updater.idle()
'''
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook("https://<>.com/" + TOKEN)
'''


if __name__ == '__main__':
    main()
