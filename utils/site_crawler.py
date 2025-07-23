# -*- coding: utf-8 -*-

from selenium import webdriver
from contextlib import contextmanager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from extensions import db
from models import Search_result,Url_resource

@contextmanager
def browser_context():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(5)
    try:
        yield browser
    finally:
        browser.quit()
        
def gimyWeb(search_key):
    searchList = []
    url = f"https://gimy.ai/search/-------------.html?wd={search_key}"
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        results = soup.find_all("a", class_="video-pic loading")
        for result in results:
            videoDict = {}
            videoDict["pic"] = result.get("data-original")
            videoDict["title"] = result.get("title")
            videoDict["url"] = "https://gimy.ai" + result.get("href")
            searchList.append(videoDict)
    return searchList

def gimyNextWeb(url):
    result=[]
    r_gimy = requests.get(url)
    if r_gimy.status_code == 200:
        soup_gimy = BeautifulSoup(r_gimy.text, "html.parser")
        # title_gimy = soup_gimy.find("h1", class_="text-overflow").contents[0]
        title_gimy = soup_gimy.find("h1", class_="text-overflow")
        content_gimy = soup_gimy.select_one("span > p")
        # pic_gimy = soup_gimy.select_one("div.details-pic > a").get("style")
        # pic_url = re.findall(r"url\((.*?)\)", pic_gimy)[0]
        if title_gimy:
            title=title_gimy.text
        else:
            title=''
        if content_gimy:
            content=content_gimy.text
        else:
            content=''
        result=[title,content]    
    return result

        
def duckWeb(search_key):
    search_url = f"https://777tv.ai/index.php/vod/search.html?wd={search_key}"
    with browser_context() as browser:
        browser.get(search_url)
        first_link = browser.find_element(By.CSS_SELECTOR, 'a[href*="/vod/detail/id/"]')
        href = first_link.get_attribute("href")
        if href:
            final_url = href
    return final_url

def fridayWeb(search_key,times=1):
    url = f"https://video.friday.tw/search?key={search_key}"
    searchList=[]
    with browser_context() as browser:
            # times=2
            while times:
                browser.get(url)
                pageSource = browser.page_source
                soup = BeautifulSoup(pageSource,"html.parser")
                datas=soup.select("div.search-item-cover a[href]")
                if datas:
                    # print(datas,search_key)
                    for result in datas:
                        videoDict = {}
                        videoDict["title"] = result.find("img").get("alt")
                        if search_key in videoDict["title"]:
                            videoDict["pic"] = result.find("img").get("src")
                            videoDict["url"] = "https://video.friday.tw" + result.get("href")
                            searchList.append(videoDict)
                        else:
                            videoDict = {}
                    times=0
                else:
                    times=times-1
    return searchList

def fridayNextWeb(url):
    result=[]
    with browser_context() as browser:        
        browser.get(url)
        pageSource = browser.page_source
        soup_fri = BeautifulSoup(pageSource,"html.parser")
        # print(soup_fri)
        title_fri = soup_fri.find("h1", class_="film-title-h1")
        content_fri=soup_fri.find("p", class_="info-item-text")
        # print(title_fri)
        result=[title_fri.text,content_fri.text]
    return result

def youtubWeb(target):
    yt_search = f"https://www.youtube.com/results?search_query={target}預告片"
    with browser_context() as browser:
        browser.get(yt_search)
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "video-title")))
        
        yt_element = browser.find_elements(By.CSS_SELECTOR,"a#video-title")[0]
        final_url = yt_element.get_attribute("href")
    return final_url

def storeTodb(target,result_data,url_sources):
    print("===============================",target)
    key = Search_result.query.filter_by(keyword=target).first()
    if not key:
        new_keyword = Search_result(
                        keyword=target,
                        title=result_data["title"],
                        content=result_data["content"],
                        pic_url=result_data["pic"],
                        yt=result_data["yt"]
                    )
        db.session.add(new_keyword)
        db.session.commit()             
              
        new_Url = Url_resource(
                    keyword = target,
                    gimy = url_sources["gimy"],
                    friday = url_sources["friday"],
                    duck = url_sources["duck"],
                    netflix = url_sources["netflix"]
                    )
        db.session.add(new_Url)
        db.session.commit()
    
def checkDB(target):
    searchResult = Search_result.query.filter_by(keyword=target).first()
    if searchResult:
        DB_result_data = {
            "title": searchResult.title,
            "content": searchResult.content,
            "pic": searchResult.pic_url,
            "yt": searchResult.yt
        }
        
        urlResult = Url_resource.query.filter_by(keyword=target).first()
        DB_url_sources = {
            "gimy": urlResult.gimy,
            "friday": urlResult.friday,
            "duck": urlResult.duck,
            "netflix": "https://www.netflix.com/tw/title/81040344"
        }
        return DB_result_data,DB_url_sources
    else:
        return None
        
    
    