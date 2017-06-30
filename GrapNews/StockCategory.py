
import MySQLdb
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from pyexcel_xls import get_data
import sys,os
import xlrd


tablesSql = """CREATE TABLE IF NOT EXISTS Category (
  id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY unique,
  category_name VARCHAR(30) NOT NULL,
  category_code VARCHAR(10),
  category_attr VARCHAR(4) );"""

tablesCategorySql = """CREATE TABLE IF NOT EXISTS StockToCategory (
  id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY unique,
  category_id INTEGER NOT NULL,
  stock_id INTEGER );"""

industryBaseUrl = "http://www.sse.com.cn"
industryUrl = "http://www.sse.com.cn/assortment/stock/areatrade/area/"
matchText ="""<a target="_blank"  [\s\S]*?</a>"""
matchUrl = """href=[\s\S]*?>"""
matchDes = """>[\s\S]*?<"""

class RegionItem(object) :
    regionName = ""
    regionUrl = ""
    def __init__(self,regionName,regionUrl):
        self.regionName = regionName
        self.regionUrl = regionUrl

class StockItem(object):
    stockName = ""
    stockFullName = ""
    stockCode = ""
    stockRegion = ""
    def __init__(self,stockName ,stockCode,stockFullName,stockRegion):
        self.stockFullName = stockFullName
        self.stockCode = stockCode
        self.stockName = stockName
        self.stockRegion = stockRegion

def createStockCategoryTable(sql):
    connect = MySQLdb.connect(host='localhost', user='root', passwd='hushuaibing', db='Stock', charset='utf8')
    cursor = connect.cursor()
    cursor.execute(sql)
    cursor.close()
    connect.close()

def requestHtmlContent(requestUrl):
    respont = requests.get(url=requestUrl);
    respont.encoding = 'utf-8'
    return respont.text

def match(text,matchTxt):
    pattern = re.compile(matchTxt)
    return pattern.findall(text)

def findAllRegion():
    allRegion = match(requestHtmlContent(industryUrl),matchText)
    regions = []
    for child in allRegion:
        region = RegionItem("","")
        name = match(child,matchDes)[0][1:][:-1]
        url = match(child,matchUrl)[0].rstrip('href=').rstrip('">')[6:]
        region.regionName = name
        region.regionUrl = industryBaseUrl + url
        regions.append(region)
    return regions

def save_category_to_database(regions):
    connect = MySQLdb.connect(host='localhost', user='root', passwd='hushuaibing', db='Stock', charset='utf8')
    cursor = connect.cursor()
    for region in regions:
        print region.regionName + region.regionUrl
        selectSql = "select * from Category where category_name ='" + region.regionName +"'";
        rowNums = cursor.execute(selectSql)
        if rowNums == 0:
            sql = "insert into Category (category_name,category_attr) values ('" + region.regionName +  "','1');"
            cursor.execute(sql)
        else:
            print 'This stock code has exits. ' + str(rowNums)
    cursor.close()
    connect.commit()
    connect.close()


def requestRegionStock(page_url):
    driver = webdriver.PhantomJS()
    driver.get(page_url)
    time.sleep(3)
    text = driver.page_source
    soup = BeautifulSoup(text, 'html.parser')
    stockCodes = []
    for child in soup.find_all(attrs={'class': 'isClickTr'}):
        stockCodes.append(child.find(['a']).string)
    return stockCodes


def save_relation_to_database(stockCode,categoryName):
    connect = MySQLdb.connect(host='localhost', user='root', passwd='hushuaibing', db='Stock', charset='utf8')
    cursor = connect.cursor()
    stockIdSql = "select id from StockList where stock_code = '" + stockCode +"'"
    categoryIdSql = "select id from Category where category_name = '" + categoryName +"'"
    cursor.execute(stockIdSql)
    results = cursor.fetchall()
    stockId = ""
    categoryId = ""
    for row in results:
        stockId = row[0]
    cursor.execute(categoryIdSql)
    results = cursor.fetchall()
    for row in results:
        categoryId = row[0]
    print 'stockCode = ' + stockCode + ' stockId = ' + str(stockId) + ' categoryName = ' + categoryName + '  categoryId = ' + str(categoryId)
    if str(stockId).strip() != "" and str(categoryId).strip() != None and str(stockId).strip() != None:
        cursor.execute("insert into StockToCategory set category_id = " + str(categoryId) +",stock_id =" + str(stockId))
    cursor.close()
    connect.commit()
    connect.close()

def readExcel(path):
    xl_data = xlrd.open_workbook(path)
    print xl_data.sheet_names()
    sheet = xl_data.sheet_by_index(0)
    print sheet.name,sheet.nrows,sheet.ncols
    stocks = []
    for index in range(1,sheet.nrows):
        code = sheet.cell(index,0).value
        name = sheet.cell(index,1).value
        fullname = sheet.cell(index,2).value
        region = sheet.cell(index,16).value
        stock = StockItem(stockCode=code,stockFullName=fullname,stockName=name,stockRegion=region)
        stocks.append(stock)
    return stocks

def save_xls_to_database(stocks):
    connect = MySQLdb.connect(host='localhost', user='root', passwd='hushuaibing', db='Stock', charset='utf8')
    cursor = connect.cursor()

    for stockItem in stocks:
        selectSql = "select stock_code from StockList where stock_code ='" + stockItem.stockCode + "'";
        rowNums = cursor.execute(selectSql)
        if rowNums == 0:
            sql = "insert into StockList (stock_code,stock_name,stock_full_name,stock_pinyin_name) values ('" + stockItem.stockCode + "','" + stockItem.stockName + "','" + stockItem.stockFullName + "','   ');"
            cursor.execute(sql)
        else:
            print 'This stock code has exits. ' + str(rowNums)
        stockIdSql = "select id from StockList where stock_code = '" + stockItem.stockCode +"'"
        categoryIdSql = "select id from Category where category_name = '" + stockItem.stockRegion +"'"
        cursor.execute(stockIdSql)
        results = cursor.fetchall()
        stockId = ""
        categoryId = ""
        for row in results:
            stockId = row[0]
        cursor.execute(categoryIdSql)
        results = cursor.fetchall()
        for row in results:
            categoryId = row[0]
        print 'stockCode = ' + stockItem.stockCode + ' stockId = ' + str(stockId) + ' categoryName = ' + stockItem.stockRegion + '  categoryId = ' + str(categoryId)
        if str(stockId).strip() != "" and str(categoryId).strip() != None and str(stockId).strip() != None:
            cursor.execute("insert into StockToCategory set category_id = " + str(categoryId) +",stock_id =" + str(stockId))

    cursor.close()
    connect.commit()
    connect.close()

createStockCategoryTable(tablesSql)
createStockCategoryTable(tablesCategorySql)
regions = findAllRegion()
save_category_to_database(regions)
for child in regions:
    stockCodes = requestRegionStock(child.regionUrl)
    for stockChild in stockCodes:
        save_relation_to_database(stockCode = stockChild,categoryName = child.regionName)

path = os.getcwd() + '/stock.xlsx'
stocks = readExcel(path)
save_xls_to_database(stocks)
