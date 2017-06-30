
import MySQLdb
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import time

conceptUrl = 'http://finance.sina.com.cn/stock/sl/#industry_1'

matchUrl = """href=[\s\S]*?>"""
matchDes = """>[\s\S]*?<"""

class ConceptItem(object) :
    conceptName = ""
    conceptUrl = ""
    def __init__(self,conceptName,conceptUrl):
        self.conceptName = conceptName
        self.conceptUrl = conceptUrl

def match(text,matchTxt):
    pattern = re.compile(matchTxt)
    return pattern.findall(text)

def requestAllHtmlContent(page_url):
    driver = webdriver.PhantomJS()
    driver.get(page_url)
    time.sleep(20)
    return driver.page_source

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

def requestConceptData(page_url):
    text = requestAllHtmlContent(page_url)
    soup = BeautifulSoup(text, 'html.parser')
    concepts = []

    for child in soup.find_all(attrs={'class': 'datatbl'}):
        trs = child.find(['tbody']).find_all(['tr'])
        for tr_child in trs:
            concept = ConceptItem("", "")
            url = tr_child.find(['a']).get('href')
            name = tr_child.find(['a']).text
            concept.conceptName = name
            concept.conceptUrl = url
            concepts.append(concept)
    return concepts


def save_category_to_database(concepts):
    connect = MySQLdb.connect(host='localhost', user='root', passwd='hushuaibing', db='Stock', charset='utf8')
    cursor = connect.cursor()
    for region in concepts:
        print region.conceptName + region.conceptUrl
        selectSql = "select * from Category where category_name ='" + region.conceptName +"'";
        rowNums = cursor.execute(selectSql)
        if rowNums == 0:
            sql = "insert into Category (category_name,category_attr) values ('" + region.conceptName +  "','2');"
            cursor.execute(sql)
        else:
            print 'This stock category has exits. ' + str(rowNums)
    cursor.close()
    connect.commit()
    connect.close()

def requestDetailData(page_url,concept_name):
    text = requestAllHtmlContent(page_url)
    soup = BeautifulSoup(text, 'html.parser')
    print soup.find(attrs={'class':'tbl_wrap'})
    print soup.find(attrs={'class':'tbl_wrap'}).find(['tbody']);

concepts = requestConceptData(conceptUrl)
save_category_to_database(concepts)

for child in concepts:
    print child.conceptUrl,child.conceptName
    requestDetailData(child.conceptUrl,child.conceptName)
