from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
import base64
import requests
import os
import time

MAX_RESULTS = 5
WAIT_TIME = 10

def createDriver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # prefs = {"profile.managed_default_content_settings.images":2}
    # chrome_options.headless = True

    # chrome_options.add_experimental_option("prefs", prefs)
    myDriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    return myDriver

def getGoogleHomepage(driver: webdriver.Chrome) -> str:
    driver.get("https://www.google.com")
    return driver.page_source

def getHulan(driver: webdriver.Chrome, topic: str, len: str) -> dict:
    driver.get("https://howtobullshit.me")

    topic_pos = driver.find_element_by_id("topic")
    minlen_pos = driver.find_element_by_id("minlen")

    topic_pos.send_keys(topic)
    minlen_pos.send_keys(len)

    driver.find_element_by_id("btn-get-bullshit").click()
    time.sleep(3)
    content = driver.find_element_by_id("content")

    myDict = {
        "topic": topic,
        "len": len,
        "text": content.text
    }

    return myDict

def drawLots()-> dict:
    # 載入資料庫
    mongo_client_ccsue = MongoClient(os.getenv("MONGO_URL"))
    db = mongo_client_ccsue.get_database('Sensoji')
    record = db['Omikuji']

    # 隨機抽取
    random = record.aggregate(
        [{"$sample": { "size": 1 }}]
    )

    for item in random:
        myDict = {
            "luck": item["luck"],
            "content": item["content"],
            "src": item["src"]
        }

    return myDict

def getHentai(driver: webdriver.Chrome, name: str) -> list:
    driver.get("https://www.wnacg.com/albums.html")

    input = driver.find_element(By.NAME, "q")
    input.send_keys(name)
    input.submit()

    element = WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "title"))
    )
    
    myList = []
    for index, i in enumerate(element):
        if index == MAX_RESULTS:
            break
        obj = i.find_element(By.TAG_NAME, "a")
        title = obj.get_attribute("title").replace('<em>', '').replace('</em>', '')
        href = obj.get_attribute("href").replace('<em>', '').replace('</em>', '')
        
        myDict = {
            "title": title,
            "src": href
        }
        myList.append(myDict)

    return myList

def getImageHentai(driver: webdriver.Chrome, url: str) -> list:
    driver.get("https://soutubot.moe")
    
    # 拿到影像數據
    response = requests.get(url)
    image_data = response.content

    # 將二進位影像數據轉換為 Base64 編碼格式
    image_data_base64 = base64.b64encode(image_data).decode('utf-8')

    script = f"""
    function simulatePasteImage(base64Image) {{
        // 將 Base64 字符串轉換為 Blob
        var byteCharacters = atob(base64Image);
        var byteNumbers = new Array(byteCharacters.length);
        for (var i = 0; i < byteCharacters.length; i++) {{
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }}
        var byteArray = new Uint8Array(byteNumbers);
        var blob = new Blob([byteArray], {{ type: 'image/png' }});
        var file = new File([blob], 'pasted-image.png', {{ type: 'image/png' }});

        // 創建剪貼板事件
        var clipboardData = new DataTransfer();
        clipboardData.items.add(file);
        
        var pasteEvent = new ClipboardEvent('paste', {{
            clipboardData: clipboardData,
            bubbles: true,
            cancelable: true
        }});

        // 觸發 paste 事件
        document.dispatchEvent(pasteEvent);
    }}

    // 執行模擬粘貼影像的函數
    simulatePasteImage("{image_data_base64}");
    """

    # 執行 JavaScript
    driver.execute_script(script)

    # 按下搜尋
    WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_element_located((By.CLASS_NAME, "el-button--primary"))
    ).click()
    
    # 找到本子
    elements = WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "card-2.rounded-md.p-3.w-full"))
    )

    # 抓取 title & url
    myList = []
    for index, e in enumerate(elements):
        if index == MAX_RESULTS:
            break   
        href = e.find_element(By.XPATH, "//a[contains(text(), '详情页')]").get_attribute("href")
        title = e.find_element(By.TAG_NAME, "span").text
        myDict = {
            "title": title,
            "src": href
        }
        myList.append(myDict)

    return myList

def doBackgroundTask(inp):
    print("Doing background task")
    print(inp.msg)
    print("Done")
