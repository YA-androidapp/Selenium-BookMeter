#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 読書メーターのユーザーページから、読んだ本のタイトル一覧を取得する
######################################################################

from bs4 import BeautifulSoup  # pip install beautifulsoup4 && pip install lxml
import datetime
import os
import re
import time
from selenium import webdriver  # pip install selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options


# const
user = '888888'
hostbm = 'https://bookmeter.com'
url = hostbm+'/users/'+user+'/books/read'
hosthm = 'https://www.hmv.co.jp'

cd = os.path.expanduser(
    '~\\OneDrive\\ドキュメント\\works\\Python\\Sele\\Sele-BookMeter'
)
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

    if url.startswith('/'):
        url = hostbm + url

    global fox
    fox.get(url)
    if(url.startswith(hostbm)):
        WebDriverWait(fox, 60).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'bm-pagination-notice')
            )
        )

    # if(url.startswith(hosthm)):
    #     WebDriverWait(fox, 60).until(
    #         EC.presence_of_element_located(
    #             (By.CLASS_NAME, 'rights')
    #         )
    #     )

    html_post = fox.page_source
    return(html_post)


# Seleniumを起動
from selenium.webdriver import Firefox
binary = 'C:\\Program Files\\Mozilla Firefox ESR\\firefox.exe'
binary = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'

# conda install -c conda-forge geckodriver
options = Options()
options.binary_location = binary
# options.add_argument('-headless')
fox = webdriver.Firefox(firefox_options=options)
fox.set_page_load_timeout(60)
print('fox')

fox.set_window_size(1280, 240)
print('set_window_size')

# パース
soup = BeautifulSoup(get_source(url), features='lxml')
html_post_title = soup.title.string
print(html_post_title)

# 最終ページを取得
lastpage = int(
    soup.find(
        'a',
        class_='bm-pagination__link',
        text=re.compile('最後')
    ).get('href').split('read?page=')[1]


)


# 本のタイトルを取得して、リストに追加
list_title = []
list_isbn = []

isbnpattern = '([0-9]{13})'
isbnpatternre = re.compile(isbnpattern)

url_sub = url
for p in range(lastpage):
    # 進捗状況
    print(str(int(100*(p+1)/lastpage))+'%')  # , end='\t')
    print('p:'+str(p), end='\t')
    print(' url_sub:'+url_sub, end='\n')

    items = soup.select('div.thumbnail__cover')
    for item in items:
        title = ''
        isbn = ''
        try:
            img = item.img
            title = img.get('alt')

            a = item.find('a')
            uri = a.get('href')
            print(hostbm + uri, end='\t')
            soupsub = BeautifulSoup(get_source(uri), features='lxml')
            urihm = soupsub.find(
                'li',
                attrs={'class', 'shop-list__item shop-list__item--hmvbooks'}
            ).find('a').get('href')
            souphm = BeautifulSoup(get_source(urihm), features='lxml')
            result = isbnpatternre.findall(souphm.title.text)
            isbn = ''
            if result:
                isbn = result[0]
            print(isbn, end='\n')
        except:
            pass
        else:
            list_title.append(title)
            list_isbn.append(isbn)
        finally:
            print('', end='\n')

    if p == lastpage:
        break

    url_sub = url + '?page=' + str(p+2)
    print('p:'+str(p)+' url_sub:'+url_sub)
    time.sleep(1)

    soup = BeautifulSoup(get_source(url_sub), features='lxml')


# 後片付け
fox.close()
try:
    fox.quit()
except:
    pass


# リストを整形
# list_title.sort()
# list_title.reverse()


# 出力
with open(listfile_path, 'a') as file:
    for index in range(len(list_title)):
        file.write((list_title[index]) + '\t' + (list_isbn[index]))
