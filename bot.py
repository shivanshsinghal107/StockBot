from telegram.ext import Updater, CommandHandler
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from pandas_datareader import data as pdr
from io import BytesIO
import os


# function to get latest finance news articles
def get_news():
    res = requests.get("https://www.cnbc.com/world/?region=world")
    soup = BeautifulSoup(res.text, 'html.parser')
    news = soup.select('#MainContent > div:nth-child(2) > div > div > div:nth-child(6) > div.PageBuilder-col-6.PageBuilder-col')[0]
    links = news.find_all('a')

    headlines = []
    for link in links:
        if len(link.text) > 30:
            headlines.append(link.text)

    hrefs = []
    for link in links:
        if len(link.text) > 30:
            hrefs.append(link['href'])

    top5 = "Here's your latest finance news articles:\n"
    for i in range(0, 5):
        top5 += headlines[i] + "\n" + hrefs[i] + "\n"
    return top5

# function to get top 10 articles from quantopian
def get_quantopian_articles():
    res = requests.get("https://www.quantopian.com/posts")
    soup = BeautifulSoup(res.text, "html.parser")
    posts = soup.select("#search-results")[0]
    top10 = posts.findAll('div', {'class': 'post-title'})[:10]

    lines = []
    for i in top10:
        lines.append(i.text.strip())

    hrefs = []
    for i in top10:
        for a in i.find_all('a', href = True):
            hrefs.append(a['href'].strip())

    links = []
    for href in hrefs:
        link = 'https://www.quantopian.com' + href
        links.append(link)

    top10 = "Here's the top 10 articles from Quantopian:\n"
    for i in range(0, 10):
        top10 += lines[i] + "\n" + links[i] + "\n"
    return top10

# function to get top 10 articles from quantocracy
def get_quantocracy_articles():
    headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
    res = requests.get("https://quantocracy.com/", headers = headers)
    soup = BeautifulSoup(res.text, "html.parser")
    posts = soup.select("#qo-mashup")[0]
    top10 = posts.findAll('a', {'class': 'qo-title'})[:10]

    lines = []
    for i in top10:
        lines.append(i.text.strip())

    links = []
    for i in top10:
        links.append(i['href'])

    top10 = "Here's the top 10 articles from Quantocracy:\n"
    for i in range(0, 10):
        top10 += lines[i] + "\n" + links[i] + "\n"
    return top10

# function to get top 10 articles from quantstart systematic trading
def get_quantstart_articles():
    res = requests.get("https://www.quantstart.com/articles/topic/systematic-trading/")
    soup = BeautifulSoup(res.text, "html.parser")
    posts = soup.select("body > div > section.mb-2 > div")[0]

    lines = []
    for post in posts.findAll('p')[:10]:
        lines.append(post.text)

    hrefs = []
    for href in posts.findAll('a')[:10]:
        hrefs.append(href['href'])

    links = []
    for href in hrefs:
        link = 'https://www.quantstart.com' + href
        links.append(link)

    top10 = "Here's the top 10 articles from Quantstart Systematic Trading:\n"
    for i in range(0, 10):
        top10 += lines[i] + "\n" + links[i] + "\n"
    return top10

# function to get stock prices of indexes of given country
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

# function to get commodity price for the given commodity
def commodity_price(commodity):
    # load csv and get dataframe
    df = pd.read_csv('commodities.csv')

    # check which commodity user has entered and get it
    indice = df[df['Name'].str.contains(commodity.upper())].reset_index()
    indice.drop(columns = ['index'], inplace = True)

    # if indice is empty that means the given commodity is not in the database
    if(indice.empty):
        return " "

    # webpage having the commodity's stock price
    url = indice['URL'][0]

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

    index = "Currently the " + str(indice['Name'][0]) + " stands at " + str(price) + " " + str(currency) + "\n"

    return index


def start(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = '''
Use these commands to use the bot:
/news - get the latest finance news articles
/quantopian - get top articles of Algorithmic Trading from Quantopian
/alpha - get top algo trading models
/quantstart - get top articles of Algorithmic Trading from Quantstart
/country - get the list of countries the bot has the data for
/index - get real time price & chart of stock indices of a given country
/comlist - get the list of commodities the bot has the data for
/com - get real time price of a given commodity
/help - get list of commands of the bot''')

# function to display top 5 finance news headlines
def get_top_news(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Just a sec! Fetching latest finance news!")
    top5 = get_news()
    context.bot.send_message(chat_id = update.effective_chat.id, text = top5)

# function to display top 10 quantopian articles
def get_quantopian(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Just a sec! Fetching the top articles!")
    top10 = get_quantopian_articles()
    context.bot.send_message(chat_id = update.effective_chat.id, text = top10)

# function to display top 10 quantocracy articles
def get_quantocracy(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Just a sec! Fetching the top articles!")
    top10 = get_quantocracy_articles()
    context.bot.send_message(chat_id = update.effective_chat.id, text = top10)

# function to display top 10 quantstart articles
def get_quantstart(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Just a sec! Fetching the top articles!")
    top10 = get_quantstart_articles()
    context.bot.send_message(chat_id = update.effective_chat.id, text = top10)

# function to display country list the bot has
def get_country_list(update, context):
        df = pd.read_csv('stock_indices.csv')
        countries = "Here is your country list:\n"
        # really smart move
        for c in df['Country']:
            countries += c + "\n"
        context.bot.send_message(chat_id = update.effective_chat.id, text = countries)

# function to display commodities list the bot has
def get_commodity_list(update, context):
    df = pd.read_csv('commodities.csv')
    commodities = "Here are your commodities:\n"
    for c in df['Name']:
        commodities += c + "\n"
    context.bot.send_message(chat_id = update.effective_chat.id, text = commodities)

# function to display stock prices of stock indexes for a given country
def get_stock_prices(update, context):
    if context.args == []:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Type in the country name as the KeyWord along with the /index command')
        return
    context.bot.send_message(chat_id=update.effective_chat.id, text= "Just a sec! Finding related info!")
    country = " ".join(context.args)
    stock_indices = index_price(country)
    if(stock_indices == " "):
        context.bot.send_message(chat_id=update.effective_chat.id, text= "Sorry, I don't have data for this. Take a look at the country list by command /country.")
    else:
        df = pd.read_csv('stock_indices.csv')
        yf.pdr_override()
        df['Symbol'] = df['URL'].apply(lambda x: '^'+x.split("%5E")[1][:-1] if "%5E" in x else x.split("quote/")[1][:-1])
        index = df.loc[df['Country'] == country.upper()].index.values
        data = pdr.get_data_yahoo(df.loc[index[0], 'Symbol'], start='2019-11-01')

        fig = plt.figure()
        ax = (data['Close'] / data['Close'].iloc[0] * 100).plot(figsize=(15, 6))
        plt.xlabel('DATE')
        plt.ylabel('PRICE')
        plt.title(df.loc[df['Country'] == country.upper()]['Indices'].values[0])
        plt.fill_between(data.index, data.Close)
        buffer = BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        context.bot.send_message(chat_id=update.effective_chat.id, text = stock_indices)
        context.bot.send_photo(chat_id = update.effective_chat.id, photo = buffer)

# function to display commodity price for a given commodity
def get_commodity_prices(update, context):
    if context.args == []:
        context.bot.send_message(chat_id = update.effective_chat.id, text = 'Type in the commodity as the KeyWord along with the /com command.')
        return
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Just a sec! Finding related info!")
    commodity = " ".join(context.args)
    commodities = commodity_price(commodity)
    if(commodities == " "):
        context.bot.send_message(chat_id=update.effective_chat.id, text= "Sorry, I don't have data for this. Take a look at the commodity list by command /comlist.")
    else:
        context.bot.send_message(chat_id = update.effective_chat.id, text = commodities)

# function to get list of all commands
def get_commands(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = '''
/news - get the latest finance news articles
/quantopian - get top articles of Algorithmic Trading from Quantopian
/alpha - get top algo trading models
/quantstart - get top articles of Algorithmic Trading from Quantstart
/country - get the list of countries the bot has the data for
/index - get real time price & chart of stock indices of a given country
/comlist - get the list of commodities the bot has the data for
/com - get real time price of a given commodity
/help - get list of commands of the bot''')




def main():
    TOKEN = os.getenv("TOKEN")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dp.add_handler(start_handler)
    news_handler = CommandHandler('news', get_top_news)
    dp.add_handler(news_handler)
    quantopian_handler = CommandHandler('quantopian', get_quantopian)
    dp.add_handler(quantopian_handler)
    quantocracy_handler = CommandHandler('alpha', get_quantocracy)
    dp.add_handler(quantocracy_handler)
    quantstart_handler = CommandHandler('quantstart', get_quantstart)
    dp.add_handler(quantstart_handler)
    stock_handler = CommandHandler('index', get_stock_prices)
    dp.add_handler(stock_handler)
    country_handler = CommandHandler('country', get_country_list)
    dp.add_handler(country_handler)
    commodity_handler = CommandHandler('comlist', get_commodity_list)
    dp.add_handler(commodity_handler)
    commodity_price_handler = CommandHandler('com', get_commodity_prices)
    dp.add_handler(commodity_price_handler)
    command_handler = CommandHandler('help', get_commands)
    dp.add_handler(command_handler)
    PORT = int(os.environ.get('PORT', 5000))
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook("https://aryavarta-bot.herokuapp.com/" + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
