import MySQLdb
import time
import requests
import sys
from bs4 import BeautifulSoup

stockDataBaseUrl = "http://www.yz21.org/stock/info/"
tablesSql = """CREATE TABLE IF NOT EXISTS StockList (
  id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY unique,
  stock_name TEXT NOT NULL,
  stock_code TEXT NOT NULL,
  stock_full_name TEXT NOT NULL,
  stock_pinyin_name TEXT NOT NULL);"""


class StockItem(object) :
    stockName=""
    stockCode = ""
    stockFullName = ""
    stockPinYin = ""
    def __init__(self,stockName , stockCode,stockFullName,stockPinYin):
        self.stockName = stockName
        self.stockCode = stockCode
        self.stockFullName = stockFullName
        self.stockPinYin = stockPinYin

def createSharesTables():
    # connect = MySQLdb.connect(host='xcoy6rr9.zzcdb.dnstoo.com', port=6079 ,user='stock_root', passwd='stock_root',db='stock_888',charset='utf8')
    connect = MySQLdb.connect(host='localhost', user='root', passwd='hushuaibing', db='Stock', charset='utf8')
    cursor = connect.cursor()
    cursor.execute(tablesSql)
    cursor.close()

def request_stock_pageUrl():
    respont = requests.get(url=stockDataBaseUrl)
    respont.encoding = 'utf-8'
    soup = BeautifulSoup(respont.text, 'html.parser')
    pagestock = soup.find(attrs={'class': 'pagestock'})
    pageUrl = []
    pageUrl.append(stockDataBaseUrl)
    for childPage in pagestock.find_all(["a"]):
        pageUrl.append(stockDataBaseUrl + childPage.get("href"))
    return pageUrl

def request_page_stock_list(page_url):
    print ('page url = ' + page_url)
    respont = requests.get(url=page_url)
    respont.encoding = 'utf-8'
    soup = BeautifulSoup(respont.text, 'html.parser')
    stockItems = []
    index = 0
    item = ["","","","",""]
    for child in soup.find(attrs={'class':'stockBlock'}).find_all(["td"]):
        if index > 5:
            item[index%5] = child.string
            if index % 5 == 4:
                stockItems.append(StockItem(stockCode=item[1],stockName=item[2],stockFullName=item[3],stockPinYin=item[4]))
        index = index + 1
    return stockItems

def save_to_database(stockItems):
    connect = MySQLdb.connect(host='localhost', user='root', passwd='hushuaibing', db='Stock', charset='utf8')
    cursor = connect.cursor()
    for stockItem in stockItems:
        print stockItem.stockCode + stockItem.stockName + stockItem.stockFullName + stockItem.stockPinYin
        selectSql = "select stock_code from StockList where stock_code ='" + stockItem.stockCode +"'";
        rowNums = cursor.execute(selectSql)
        if rowNums == 0:
            sql = "insert into StockList (stock_code,stock_name,stock_full_name,stock_pinyin_name) values ('" + stockItem.stockCode +  "','" +stockItem.stockName +  "','" +stockItem.stockFullName + "','" +stockItem.stockPinYin + "');"
            cursor.execute(sql)
        else:
            print 'This stock code has exits. ' + str(rowNums)
    cursor.close()
    connect.commit()
    connect.close()

createSharesTables()
reload(sys)
sys.setdefaultencoding('utf-8')
pageUrls = request_stock_pageUrl()
for url in pageUrls:
    print  "url = " + url
    stockItems = request_page_stock_list(url)
    save_to_database(stockItems)


