
import MySQLdb
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import time

conceptUrl = 'http://stockapp.finance.qq.com/mstats/?mod=all#mod=list&id=bd_ind&module=BD&type=01&sort=8&page=1&max=80'
addresUrl = 'http://stockapp.finance.qq.com/mstats/?mod=all#mod=list&id=bd_rgn&module=BD&type=03'

conceptDetailBaseUrl = 'http://stockapp.finance.qq.com/mstats/?mod=all#mod=list&max=80&page=1&'

matchUrl = """href=[\s\S]*?>"""
matchDes = """>[\s\S]*?<"""


tablesSql = """CREATE TABLE IF NOT EXISTS Category (
  id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY unique,
  category_name VARCHAR(30) NOT NULL,
  category_code VARCHAR(10),
  category_attr VARCHAR(4) );"""

tablesCategorySql = """CREATE TABLE IF NOT EXISTS StockToCategory (
  id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY unique,
  category_id INTEGER NOT NULL,
  stock_id INTEGER );"""


class ConceptItem(object) :
    conceptName = ""
    conceptUrl = ""
    def __init__(self,conceptName,conceptUrl):
        self.conceptName = conceptName
        self.conceptUrl = conceptUrl


def createStockCategoryTable(sql):
    connect = MySQLdb.connect(host='localhost', user='root', passwd='hushuaibing', db='Stock', charset='utf8')
    cursor = connect.cursor()
    cursor.execute(sql)
    cursor.close()
    connect.close()

def match(text,matchTxt):
    pattern = re.compile(matchTxt)
    return pattern.findall(text)

def requestAllHtmlContent(page_url):
    driver = webdriver.PhantomJS()
    driver.get(page_url)
    time.sleep(30)
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
        rowNums = cursor.execute("select * from StockToCategory where category_id = " + str(categoryId) +" and stock_id =" + str(stockId))
        if rowNums <= 0 :
            cursor.execute("insert into StockToCategory set category_id = " + str(categoryId) +",stock_id =" + str(stockId))
        else:
            print 'Stock Category has exit'
    cursor.close()
    connect.commit()
    connect.close()


def requestConceptData(page_url,index):
    try:
        print page_url,index
        page_url = str(page_url).replace('page=' + str(index - 1), 'page=' + str(index))
        text = requestAllHtmlContent(page_url)
        soup = BeautifulSoup(text, 'html.parser')
        concepts = []
        list_body = soup.find(attrs={'id':'list-body'})
        lis = list_body.find_all(['li'])
        for child in lis:
            a_child = child.find(['a'])
            concept = ConceptItem("", "")
            url = conceptDetailBaseUrl + str(a_child.get('listload')).replace(',','&')
            name = a_child.text
            concept.conceptName = name
            concept.conceptUrl = url
            print name
            concepts.append(concept)
        if len(lis) < 80:
            return concepts
        else:
            concepts.extend(requestConceptData(page_url,index+ 1))
            return concepts
    except AttributeError:
        print 'attribute error'
        return requestConceptData(page_url)

def save_category_to_database(concepts,category_attr):
    connect = MySQLdb.connect(host='localhost', user='root', passwd='hushuaibing', db='Stock', charset='utf8')
    cursor = connect.cursor()
    for region in concepts:
        print region.conceptName + region.conceptUrl
        selectSql = "select * from Category where category_name ='" + region.conceptName +"'";
        rowNums = cursor.execute(selectSql)
        if rowNums == 0:
            sql = "insert into Category (category_name,category_attr) values ('" + region.conceptName +  "','"+str(category_attr)+"');"
            cursor.execute(sql)
        else:
            print 'This stock category has exits. ' + str(rowNums)
    cursor.close()
    connect.commit()
    connect.close()

def requestDetailData(page_url,concept_name,index):
    try:
        page_url = str(page_url).replace('page='+str(index - 1),'page=' + str(index))
        print page_url, concept_name
        text = requestAllHtmlContent(page_url)
        soup = BeautifulSoup(text, 'html.parser')
        list_content = soup.find(attrs={'id': 'list-body'})
        lis = list_content.find_all(['li'])
        print len(lis)
        for child in lis:
            code = match(str(child.find(['a'])),matchDes)[0][1:][:-1]
            save_relation_to_database(code,concept_name)
        if len(lis) <80:
            pass
        elif index < 7:
            requestDetailData(page_url,concept_name,index + 1)
    except Exception:
        pass

def requestConceptCategory():
    createStockCategoryTable(tablesSql)
    createStockCategoryTable(tablesCategorySql)
    concepts = requestConceptData(conceptUrl,1)
    save_category_to_database(concepts,2)

    for child in concepts:
        requestDetailData(child.conceptUrl, child.conceptName, 1)

def requestAddresCategory():
    createStockCategoryTable(tablesSql)
    createStockCategoryTable(tablesCategorySql)
    concepts = requestConceptData(addresUrl,1)
    save_category_to_database(concepts,1)
    test = 1
    for child in concepts:
        print 'detail number = ' + str(test)
        requestDetailData(child.conceptUrl, child.conceptName, 1)
        test = test+ 1

def requestNotionCategory():
    createStockCategoryTable(tablesSql)
    createStockCategoryTable(tablesCategorySql)
    concepts = requestConceptData('http://stockapp.finance.qq.com/mstats/?mod=all#mod=list&id=bd_cpt&module=BD&type=02&sort=8&page=1&max=80',1)
    save_category_to_database(concepts,3)
    test = 1
    for child in concepts[140:]:
        print child.conceptUrl, child.conceptName
        requestDetailData(child.conceptUrl, child.conceptName, 1)
        test = test+ 1

def requestIndexCategory():
    createStockCategoryTable(tablesSql)
    createStockCategoryTable(tablesCategorySql)
    concepts = requestConceptData('http://stockapp.finance.qq.com/mstats/?mod=all#mod=list&id=bd_cpt&module=BD&type=02&sort=8&page=1&max=80',1)
    save_category_to_database(concepts,4)
    test = 1
    for child in concepts:
        print child.conceptUrl, child.conceptName
        requestDetailData(child.conceptUrl, child.conceptName, 1)
        test = test+1

def requestBaseCategory():
    createStockCategoryTable(tablesSql)
    createStockCategoryTable(tablesCategorySql)
    concepts = requestConceptData('http://stockapp.finance.qq.com/mstats/?mod=all#mod=list&id=bd_cpt&module=BD&type=02&sort=8&page=1&max=80',1)
    save_category_to_database(concepts,5)
    test = 1
    for child in concepts:
        print child.conceptUrl, child.conceptName
        requestDetailData(child.conceptUrl, child.conceptName, 1)
        test = test+ 1

requestNotionCategory()