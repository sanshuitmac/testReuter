from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from translate import Translator
import os

# 设置无头模式
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式
chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
chrome_options.add_argument("--no-sandbox")  # 避免沙盒问题（GitHub Actions 需要）
chrome_options.add_argument("--disable-dev-shm-usage")  # 避免共享内存问题

# 启动浏览器
driver = webdriver.Chrome(options=chrome_options)

try:
    # 访问路透社搜索页面，搜索 "China"
    driver.get("https://www.reuters.com/world/china/")
    time.sleep(5)  # 等待页面加载

    # 提取新闻标题（根据路透社搜索页面的 HTML 结构）
    titles = driver.find_elements(By.CSS_SELECTOR, "h3.search-result-title a")
    title_texts = [title.text.strip() for title in titles if title.text.strip()]  # 去掉空标题

    # 翻译标题成中文
    translator = Translator(to_lang="zh")
    translated_titles = []
    for title in title_texts[:10]:  # 限制为前 10 个标题，避免 API 限制
        try:
            translated_title = translator.translate(title)
            translated_titles.append(translated_title)
        except Exception as e:
            print(f"翻译失败: {title}, 错误: {e}")
            translated_titles.append(title)  # 如果翻译失败，保留原文

    # 确保 file 目录存在
    os.makedirs("file", exist_ok=True)

    # 保存到文件
    with open("file/china_news_titles.txt", "a", encoding="utf-8") as f:
        for title in translated_titles:
            f.write(title + "\n")

    print("新闻标题已保存到 file/china_news_titles.txt")

except Exception as e:
    print(f"发生错误: {e}")

finally:
    # 关闭浏览器
    driver.quit()
