import requests
import os
import datetime
import sys
from bs4 import BeautifulSoup

class NewsItem(object) :
    title = ""
    url = ""
    content = ""
    def __init__(self,title , url):
        self.title += title.strip()
        self.title += '\n'
        self.url = url

def getChildHtmlContent(newsItem , childUrl) :
    childRespont = requests.Session().get(url=childUrl)
    childRespont.encoding = 'utf-8'
    childSoup = BeautifulSoup(childRespont.text,'html.parser')
    print(newsItem.title)
    for child in childSoup.find(attrs={'class':'cnt_bd'}).descendants:
        if child.name == 'p':
            newsItem.content += '<p>'
            newsItem.content += child.text
            newsItem.content += '</p>'

def getChildContent(newsItem , childUrl) :
    childRespont = requests.Session().get(url=childUrl)
    childRespont.encoding = 'utf-8'
    childSoup = BeautifulSoup(childRespont.text,'html.parser')
    print(newsItem.title)
    for child in childSoup.find(attrs={'class':'cnt_bd'}).descendants:
        if child.name == 'p':
            newsItem.content += '    '
            newsItem.content += child.text
            newsItem.content += '\n'
    newsItem.content += '\n'

def writeToFile(newsItems):
    path = os.getcwd() + '/' + datetime.datetime.now().strftime('%Y-%m-%d') + '.txt'
    file = open(path, 'w+')
    for item in newsItems:
        file.write(item.title)
        file.write(item.content)
    file.close()

reload(sys)
sys.setdefaultencoding('utf-8')
newsUrl = 'http://tv.cctv.com/lm/xwlb/'
respont = requests.Session().get(url=newsUrl)
respont.encoding = 'utf-8'

print('request ' + newsUrl + ' success')
soup = BeautifulSoup(respont.text,'html.parser')

newsItems = []
for child in soup.find(attrs={'class':'right_con01'}).descendants:
    if child.name == 'a':
        item = NewsItem(title = child.text,url = child.get('href'))
        newsItems.append(item)

for item in newsItems:
    getChildContent(newsItem= item ,childUrl=item.url)

writeToFile(newsItems)



