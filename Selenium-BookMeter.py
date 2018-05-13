#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 読書メーターのユーザーページから、読んだ本のタイトル一覧を取得する
######################################################################

import bs4
# import chardet
import datetime
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# import urllib.request


# const
user = '888888'
url = 'https://bookmeter.com/users/'+user+'/books/read'

cd = os.path.expanduser('~\\OneDrive\\ドキュメント\\works\\Python\\Sele\\Sele-BookMeter')
# cd = os.path.dirname(os.path.abspath(__file__))
now = datetime.datetime.now()
listfile_name = 'list_{0:%Y%m%d%H%M%S}.txt'.format(now)
listfile_path = os.path.join(cd, listfile_name)


os.chdir(cd)
print(os.getcwd())


def get_source(url):
    '''
    URLを指定してHTMLソースを取得
    動的に生成されたソースを取るためにSeleniumを使用
    '''
    # headers = { "User-Agent" :  "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0" }
    # req = urllib.request.Request(url, None, headers)
    # request = urllib.request.urlopen(req)
    # html_post = request.read()
    # guess = chardet.detect(html_post)
    # html_post = html_post.decode(guess['encoding'])
    global fox
    fox.get(url)
    WebDriverWait(fox, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'bm-pagination-notice')))
    html_post = fox.page_source
    return(html_post)


# Seleniumを起動
# fox = webdriver.Firefox()
binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe')
fox = webdriver.Firefox(firefox_binary=binary)

fox.set_window_size(1280, 240)

# パース
soup = bs4.BeautifulSoup(get_source(url), "lxml")
html_post_title = soup.title.string
print(html_post_title)

# 最終ページを取得
lastpage = int(soup.find('a', class_='bm-pagination__link', text=re.compile('最後')).get('href').split('read?page=')[1])


# 本のタイトルを取得して、リストに追加
list_title = []

url_sub = url
for p in range(lastpage):
    print(str(int(100*(p+1)/lastpage))+'%') # 進捗状況
    print('p:'+str(p)+' url_sub:'+url_sub)
    
    imgs = soup.select('img.cover__image')
    for img in imgs:
        title = img.get('alt')
        print(title)
        list_title.append(title)
        
    if p == lastpage:
        break
        
    url_sub = url + '?page=' + str(p+2)
    print('p:'+str(p)+' url_sub:'+url_sub)
    time.sleep(1)
    
    soup = bs4.BeautifulSoup(get_source(url_sub), "lxml")


# 後片付け
fox.close()
try:
    fox.quit()
except:
    pass


# リストを整形
list_title.sort()
list_title.reverse()


# 出力
with open(listfile_path, 'a') as file:
    file.write("\n".join(list_title))
