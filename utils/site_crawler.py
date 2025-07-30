#site_crawler.py  # 將爬蟲所需的子程式集中在這個檔案，利用呼叫子函式的方式可精簡程式碼
from selenium import webdriver
from contextlib import contextmanager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from extensions import db
from models import Search_result
from sqlalchemy.exc import IntegrityError,OperationalError

import logging
logger = logging.getLogger(__name__) #記錄出錯的程式檔名

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
    try:
        r = requests.get(url, timeout=10) # 靜態網頁爬蟲沒有設定 timeout，requests 預設會無限等待，設定後超過時間會觸發Exception
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            results = soup.find_all("a", class_="video-pic loading")
            for result in results:
                videoDict = {}
                videoDict["pic"] = result.get("data-original")
                videoDict["title"] = result.get("title")
                videoDict["url"] = "https://gimy.ai" + result.get("href")
                searchList.append(videoDict)
    except Exception as e: # 例外處理主要針對訪問時產生的錯誤
        logger.error(f"gimyWeb 搜尋 '{search_key}' 時發生錯誤: {type(e).__name__}: {str(e)}", exc_info=True)
    return searchList

def gimyNextWeb(url):
    result=[]
    try:
        r_gimy = requests.get(url, timeout=10) # 靜態網頁爬蟲沒有設定 timeout，requests 預設會無限等待，設定後超過時間會觸發Exception
        if r_gimy.status_code == 200:
            soup_gimy = BeautifulSoup(r_gimy.text, "html.parser")
            title_gimy = soup_gimy.find("h1", class_="text-overflow")
            content_gimy = soup_gimy.select_one("span > p")
            if title_gimy:
                title=title_gimy.text
            else:
                title=''
            if content_gimy:
                content=content_gimy.text
            else:
                content=''
            result=[title,content]
    except Exception as e:
        logger.error(f"gimyNextWeb 訪問 '{url}' 時發生錯誤: {type(e).__name__}: {str(e)}", exc_info=True)
    return result


def duckWeb(search_key):
    search_url = f"https://777tv.ai/index.php/vod/search.html?wd={search_key}"
    href = "" # 回傳空字串後續存入資料庫/渲染頁面時防止炸掉(若nullable=False，以None存入會炸掉)
    try:
        with browser_context() as browser:
            browser.get(search_url)
            # first_link = browser.find_element(By.CSS_SELECTOR, 'a[href*="/vod/detail/id/"]')
            first_link = browser.find_elements(By.CSS_SELECTOR, 'a[href*="/vod/detail/id/"]')
            if first_link:
                href = first_link[0].get_attribute("href") or ""
            # href = first_link.get_attribute("href") or ""
    except Exception as e:
        logger.error(f"duckWeb 搜尋 '{search_key}' 時發生錯誤: {type(e).__name__}: {str(e)}", exc_info=True)
    return href

def fridayWeb(search_key,times=1):
    url = f"https://video.friday.tw/search?key={search_key}"
    searchList=[]
    try:
        with browser_context() as browser:
            while times: # 利用增加搜尋次數的設定可以提高搜尋到的機率，一但搜尋到就立刻停止繼續搜尋
                browser.get(url)
                pageSource = browser.page_source
                soup = BeautifulSoup(pageSource,"html.parser")
                datas=soup.select("div.search-item-cover a[href]")
                if datas:
                    for result in datas:
                        videoDict = {}
                        videoDict["title"] = result.find("img").get("alt") or "" # 因為if search_key in None: 會產生Exception，但添加 or "" 就可避免
                        if search_key in videoDict["title"]:
                            videoDict["pic"] = result.find("img").get("src") or ""
                            videoDict["url"] = "https://video.friday.tw" + (result.get("href") or "")
                            searchList.append(videoDict)
                        else:
                            videoDict = {}
                    times=0
                else:
                    times=times-1
    except Exception as e:
        logger.error(f"fridayWeb 搜尋 '{search_key}' 時發生錯誤: {type(e).__name__}: {str(e)}", exc_info=True)
        times=times-1
    return searchList

def fridayNextWeb(url):
    result=[]
    try:
        with browser_context() as browser:
            browser.get(url)
            pageSource = browser.page_source
            soup_fri = BeautifulSoup(pageSource,"html.parser")
            title_fri = soup_fri.find("h1", class_="film-title-h1")
            content_fri=soup_fri.find("p", class_="info-item-text")
            title = title_fri.text if title_fri else "" # 因為 None.text 會產生Exception，但添加 if title_fri else "" 就可避免
            content = content_fri.text if content_fri else ""
            result=[title,content]
    except Exception as e:
        logger.error(f"fridayNextWeb 訪問 '{url}' 時發生錯誤: {type(e).__name__}: {str(e)}", exc_info=True)
    return result

def youtubWeb(target):
    yt_search = f"https://www.youtube.com/results?search_query={target}預告片"
    final_url = ""
    try:
        with browser_context() as browser:
            browser.get(yt_search)
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "video-title")))

            yt_element = browser.find_element(By.CSS_SELECTOR,"a#video-title")
            final_url = yt_element.get_attribute("href") or ""
    except Exception as e:
        logger.error(f"youtubWeb 搜尋 '{target}' 時發生錯誤: {type(e).__name__}: {str(e)}", exc_info=True)
    return final_url

def storeTodb(target,result_data,url_sources):
    key = Search_result.query.filter_by(keyword=target).first()
    if not key:
        new_keyword = Search_result(
            keyword=target,
            title=result_data["title"] or "", # 回傳空字串後續存入資料庫時防止炸掉(若nullable=False，若為空值存入會炸掉)
            content=result_data["content"],
            pic_url=result_data["pic"],
            yt=result_data["yt"],
            gimy = url_sources["gimy"],
            friday = url_sources["friday"],
            duck = url_sources["duck"],
            netflix = url_sources["netflix"]
        )
        try:
            db.session.add(new_keyword)
            db.session.commit()
            return "success"
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"資料庫重複鍵錯誤: {str(e)}", exc_info=True)
            return "error_duplicate"
        except OperationalError as e:
            db.session.rollback()
            logger.error(f"資料庫操作錯誤: {str(e)}", exc_info=True)
            return "error_DB_Link_Syntax"
        except Exception as e:
            db.session.rollback()
            logger.error(f"storeTodb 儲存 '{target}' 時發生錯誤: {type(e).__name__}: {str(e)}", exc_info=True)
            return "error_DB"
    return "already_exists" # 若有key應該也要有回傳值

def checkDB(target):
    searchResult = Search_result.query.filter_by(keyword=target).first()
    if searchResult:
        DB_result_data = {
            "title": searchResult.title or "",
            "content": searchResult.content,
            "pic": searchResult.pic_url,
            "yt": searchResult.yt
        }
        DB_url_sources = {
            "gimy": searchResult.gimy,
            "friday": searchResult.friday,
            "duck": searchResult.duck,
            "netflix": searchResult.netflix
        }
        return DB_result_data,DB_url_sources
    else:
        return None


