import MySQLdb
import time


tablesSql = """CREATE TABLE IF NOT EXISTS StockMarket (
  id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY unique,
  stock_id TEXT NOT NULL,
  market_date TEXT NOT NULL,
  open_price TEXT ,
  close_price TEXT ,
  max_price TEXT ,
  min_price TEXT ,
  volume TEXT );"""


def createStockMarketTable():
    connect = MySQLdb.connect(host='localhost', user='root', passwd='hushuaibing', db='Stock', charset='utf8')
    cursor = connect.cursor()
    cursor.execute(tablesSql)
    cursor.close()
    connect.close()

def getCurrentDate():
    return time.time()

def getStampDate(date):
    timeArray = time.strptime(date, '%Y-%m-%d')
    timestamp = time.mktime(timeArray)
    return timestamp

def getFormatData(date):
    return time.strftime('%Y-%m-%d',time.localtime(date))

createStockMarketTable()

