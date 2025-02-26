import json
import os
import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import requests
import cloudscraper
# from bs4 import BeautifulSoup
from lxml import html

# 配置路径
REMOTE_DIR = "files/remote"
DATA_FILE = os.path.join(REMOTE_DIR, "news.json")
TG_BOT_TOKEN = "your-telegram-bot-token"
TG_CHAT_ID = "your-telegram-chat-id"


# 初始化 Selenium WebDriver
def init_driver():
    # options = Options()
    # options.add_argument(
    #     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    # options.add_argument("--headless")  # 无头模式
    # options.add_argument("--disable-gpu")  # 禁用 GPU 加速
    # options.add_argument("--no-sandbox")  # 解决 root 权限问题
    # options.add_argument("--disable-dev-shm-usage")  # 解决部分 Linux 运行问题
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    options = uc.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"  # GitHub Actions 可能需要这个
    options.headless = True  # 以无头模式运行

    driver = uc.Chrome(options=options)

    return driver


def cf():
    # 创建 cloudscraper 实例
    scraper = cloudscraper.create_scraper()

    # 获取页面
    url = "https://www.reuters.com/world/china/"
    response = scraper.get(url)

    # 获取页面 HTML
    page_html = response.text

    print(page_html[:2000])

    # 解析 HTML
    tree = html.fromstring(page_html)

    # 定义两个 XPath 表达式
    xpath_1 = "//li[contains(@class, 'list-item')]//h3[@data-testid='Heading']//a/font/font"
    xpath_2 = "//li[contains(@class, 'list-item')]//a[@data-testid='Heading']/font/font"

    # 执行 XPath 查询
    elements_1 = tree.xpath(xpath_1)
    elements_2 = tree.xpath(xpath_2)

    # 提取文本内容
    news_titles_1 = [element.text.strip() for element in elements_1]
    news_titles_2 = [element.text.strip() for element in elements_2]

    # 合并两个列表
    news_titles = news_titles_1 + news_titles_2

    # 打印新闻标题
    for title in news_titles:
        print(title)


# 爬取路透社新闻标题
def fetch_news():
    driver = init_driver()
    driver.get("https://www.reuters.com/world/china/")
    time.sleep(10)  # 等待加载
    print(driver.page_source[:2000])  # 只打印前1000个字符，防止输出过长
    # 将整个xml内容写入json

    # 使用 XPath 查找新闻标题
    xpath_1 = "//li[contains(@class, 'list-item')]//h3[@data-testid='Heading']//a/font/font"
    xpath_2 = "//li[contains(@class, 'list-item')]//a[@data-testid='Heading']/font/font"

    elements = driver.find_elements(By.XPATH, f"{xpath_1} | {xpath_2}")
    print(f"找到 {len(elements)} 个元素")
    news_titles = [element.text.strip() for element in elements if element.text.strip()]
    print(news_titles)
    driver.quit()

    return news_titles


# 读取历史数据
def load_old_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# 保存新数据
def save_new_data(news_list):
    os.makedirs(REMOTE_DIR, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=4)


# 发送 Telegram 消息
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)


# 主流程
def main2():
    old_news = set(load_old_data())
    new_news = set(fetch_news())

    # 找出新增的新闻
    added_news = new_news - old_news

    if added_news:
        message = "\n".join(f"- {news}" for news in added_news)
        print(f"*路透社 China 新闻更新:*\n{message}")
        # send_telegram_message(f"*路透社 China 新闻更新:*\n{message}")

    # 存储新的新闻标题
    save_new_data(list(new_news))


if __name__ == "__main__":
    # main()
    cf()
