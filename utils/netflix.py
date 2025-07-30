
import logging
logger = logging.getLogger(__name__) #記錄出錯的程式檔名

def netflixWeb(target):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import undetected_chromedriver as uc
    import time

    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")

    href = ""
    try:
        driver = uc.Chrome(options=options)

        url_netflix = f"https://www.google.com/search?q=netflix+{target}&hl=zh-TW&gl=TW"
        driver.get(url_netflix)
        time.sleep(2)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "zReHs")))

        results = driver.find_elements(By.XPATH, "//div[contains(@class, 'tF2Cxc')]//a[contains(@href,'www.netflix.com/tw/')]")
        for link in results:
            try:
                title_element = WebDriverWait(link, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h3"))
                )
                title = title_element.text
                if title and target in title: # 防止title為None
                    href = link.get_attribute("href")
                    if href:
                        break
            except Exception:
                continue
    except Exception as e:
         logger.error(f"netflixWeb 搜尋 '{target}' 時發生錯誤: {type(e).__name__}: {str(e)}", exc_info=True)
         return None
    finally:
        try:
            driver.quit()
        except:
            pass
    return href
