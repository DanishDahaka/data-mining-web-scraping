import requests
from bs4 import BeautifulSoup
import plotly.offline as pyo
import plotly.graph_objs as go

def make_soup(url):

    r = requests.get(url)
    soup = BeautifulSoup(r.content,"html.parser")
    return soup


def clean_soup(soup,pos):

    ls = soup.findAll("td", {"class": pos})
    ls = [i.get_text() for i in ls]
    return [i.replace(',','').replace('\xa0','') for i in ls]

#get data
soup = make_soup('https://www.coloplast.com/investor-relations/share-information/key-figures/')

""" creates html file, first time
with open("soup_coloplast.html", "w", encoding='utf-8') as text_file:
        text_file.write(str(soup)) """

# after checking the html for the values:
#td class =xl 74 -> revenue
#td class =xl 81 -> net profit
#td class = xl69 -> date

#assign values to list
revenue = clean_soup(soup,"xl74")
profit = clean_soup(soup,"xl81")
years = clean_soup(soup, "xl69")

#only first 5 elements relevant for these two lists
revenue = revenue[0:5]
profit = profit[0:5]

revenue = [int(i) for i in revenue]
profit = [int(i) for i in profit]

revenue.reverse()
profit.reverse()
years.reverse()



### plotly plotting ###

#plot revenue
trace0 = go.Scatter(x=years, y=revenue,
                    mode = 'lines+markers', name = 'revenue')

#plot profit
trace1 = go.Scatter(x=years, y=profit,
                    mode = 'lines+markers', name = 'profit')

data = [trace0,trace1]
layout = go.Layout(title='Coloplast Revenue and Profit from {} until {}'.format(years[0],years[-1]))
fig = go.Figure(data=data, layout=layout)
fig.show()

#pyo.plot(fig, filename='coloplast_linechart.html')


#print(revenue, profit, years)