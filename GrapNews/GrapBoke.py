#coding=UTF-8

import MySQLdb
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import sys
import os

contentUrl = "http://blog.sina.com.cn/s/articlelist_1215172700_0_"

def requestAllHtmlContent(page_url):
    driver = webdriver.PhantomJS()
    driver.get(page_url)
    time.sleep(3)
    return driver.page_source

def writeToFile(title , content):
    path = os.getcwd() + '/' + title + '.txt'
    file = open(path, 'w+')
    file.write(title)
    file.write(content)
    file.close()

heard = '教你炒'
reload(sys)
sys.setdefaultencoding('utf8')

a=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
for a in a[::-1]:
    contentHtml = requestAllHtmlContent(contentUrl + str(a) + ".html")
    soup = BeautifulSoup(contentHtml, 'html.parser')
    list_body = soup.find(attrs={'class':'articleList'})
    lis = list_body.find_all(attrs={'target':'_blank'})
    for child in lis:
        if heard in child.text:
            print 'title :' + child.text + ' url :' + child.get('href')
            childContentHtml = requestAllHtmlContent(child.get('href'))
            soup = BeautifulSoup(childContentHtml, 'html.parser')

            articalTitle = soup.find(attrs={'class': 'articalTitle'})
            title = articalTitle.find(['h2']).text

            articalContent = soup.find(attrs={'id': 'sina_keyword_ad_area2'})
            contentStrongs = articalContent.find_all(['font'])

            content = "\n"

            for strong in contentStrongs:
                content += '    '
                content += strong.text
                content += '\n'
                print strong.text

            writeToFile(title,content)
            print '====================================================================================='



