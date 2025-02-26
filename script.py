from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# 设置 Chrome 浏览器选项
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 无头模式
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# 初始化 WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # 打开路透社中国新闻页面
    driver.get("https://www.reuters.com/world/china/")

    # 等待页面加载
    time.sleep(10)

    # 获取新闻标题和链接
    news_elements = driver.find_elements(By.CSS_SELECTOR, "h3.story-title a")
    news_links = [element.get_attribute("href") for element in news_elements]

    # 打印新闻链接
    for title in news_elements:
        print(title)
finally:
    # 关闭浏览器
    driver.quit()
