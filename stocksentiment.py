from urllib.request import urlopen, Request #allows http requests
from bs4 import BeautifulSoup #web scraper
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

finviz_url = 'https://finviz.com/quote.ashx?t='
tickers = ['AMZN','GOOG','META']

news_tables = {} #create dictionary
for ticker in tickers:
    url = finviz_url + ticker
    #uses request to open website
    req = Request(url=url, headers={'user-agent': 'my-app'}) #
    response = urlopen(req)
    
    html = BeautifulSoup(response, features = 'html.parser') #gets website source code
    
    news_table = html.find(id='news-table') #finds in html
    news_tables[ticker] = news_table #create dictionary with ticker index

parsed_data = []
for ticker, news_table in news_tables.items(): #key-pair

    for row in news_table.findAll('tr'):
        try:
            title = row.a.get_text()
            date_data = row.td.text.strip().split(' ')
            if len(date_data) == 1:
                time = date_data[0]
            else:
                date = date_data[0]
                time = date_data[1]
            if date == "Today":
                date = date.today() # temp solution
            parsed_data.append([ticker, date, time, title])

        except AttributeError:
            print("") #if loading
df = pd.DataFrame(parsed_data, columns=['ticker', 'date', 'time', 'title'])

vader = SentimentIntensityAnalyzer()
f = lambda title: vader.polarity_scores(title)['compound']
df['compound'] = df['title'].apply(f)
df['date'] = pd.to_datetime(df.date).dt.date

mean_df = df.groupby(['ticker', 'date']).mean(numeric_only = True).unstack()

mean_df = mean_df.xs('compound', axis="columns").transpose()
mean_df.plot(kind='bar', title= 'Sentiment Analysis', figsize = (10,8))

plt.show()