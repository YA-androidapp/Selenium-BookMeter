#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 読書メーターのユーザーページから、読んだ本のタイトル一覧を取得する
######################################################################


# pip install bottle bs4 selenium

from bottle import error
from bottle import route, run
from selenium import webdriver
from selenium.webdriver.firefox.options import Options  # Chromeの場合は削除
# from selenium.webdriver.chrome.options import Options # Firefoxの場合は削除
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import bs4
# import chardet
import datetime
import os
import re
import time


##########


def init_driver():
    '''
    Seleniumを初期化する
    '''
    # Firefox
    options = Options()  # head-less
    options.set_headless()  # head-less

    binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe')
    # driver = webdriver.Firefox(firefox_binary=binary)
    # driver.set_window_size(1280, 240)
    driver = webdriver.Firefox(
        firefox_binary=binary, options=options)  # head-less
    return(driver)

    # # Chrome(head-less)
    # options = Options()
    # options.binary_location = '/app/.apt/usr/bin/google-chrome'
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # driver = webdriver.Chrome(chrome_options=options)
    # return(driver)


def get_source(fox, url):
    '''
    URLを指定してHTMLソースを取得
    動的に生成されたソースを取るためにSeleniumを使用
    '''
    fox.get(url)
    WebDriverWait(fox, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'bm-pagination-notice')))
    html_post = fox.page_source
    return(html_post)


def get_list(driver, user):
    url = 'https://bookmeter.com/users/' + user + '/books/read'

    # パース
    soup = bs4.BeautifulSoup(get_source(driver, url), "lxml")
    # html_post_title = soup.title.string
    # print(html_post_title)

    # 最終ページを取得
    lastpage = int(soup.find('a', class_='bm-pagination__link',
                             text=re.compile('最後')).get('href').split('read?page=')[1])

    # 本のタイトルを取得して、リストに追加
    list_title = []

    url_sub = url
    for p in range(lastpage):
        # print(str(int(100*(p+1)/lastpage))+'%')  # 進捗状況
        # print('p:'+str(p)+' url_sub:'+url_sub)

        imgs = soup.select('img.cover__image')
        for img in imgs:
            title = img.get('alt')
            # print(title)
            list_title.append(title)

        if p == lastpage:
            break

        url_sub = url + '?page=' + str(p+2)
        # print('p:'+str(p)+' url_sub:'+url_sub)
        time.sleep(1)

        soup = bs4.BeautifulSoup(get_source(driver, url_sub), "lxml")

    # 後片付け
    driver.close()
    try:
        driver.quit()
    except:
        pass

    # リストを整形
    list_title.sort()
    list_title.reverse()

    return (list_title)


##########


@route("/")
@route('/get/<user>')
def hello(user="1"):
    driver = init_driver()
    list_result = get_list(driver, user)
    # return "Hello, {user}".format(user=user)
    return {'titles': list_result}


@error(404)
def error404(error):
    return "Oops! {error}".format(error=error)


run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


# Copyright (c) 2018 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.
