# 依赖库：requests, beautifulsoup4
# 安装方法：pip install requests beautifulsoup4
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin


# github工作流和本地运行，产生的文件放在不同的目录。（gitignore忽略本地运行的目录的文件；工作流运行产生的文件不忽略，让其自动推送到仓库）
def create_output_directory():
    # 检查环境变量以确定当前的运行环境。github工作流产生文件放在workflow_files下
    if os.getenv('GITHUB_ACTIONS') == 'true':
        output_dir = 'files/workflow_files/'
    else:
        output_dir = 'files/local_files/'

    # 创建目录（如果不存在）
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return output_dir


def scrape_page(url,save_file):
    """抓取单页新闻并返回下一页的 URL"""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
    except requests.RequestException as e:
        print("获取页面时出错:", e)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("h3", class_="story-card__title")  # 查找新闻标题
    for article in articles:
        title = article.text.strip()  # 获取标题文本
        link = article.find("a")["href"]  # 获取文章链接
        full_link = urljoin(response.url, link)  # 转换为完整 URL
        print(title, full_link)
        # 若要保存数据，可以修改为写入文件，例如：
        with open(save_file, "a") as f:
            f.write(title + " " + full_link + "\n")

    next_link = soup.find("a", rel="next")  # 查找下一页链接
    if next_link:
        next_href = next_link["href"]
        return urljoin(response.url, next_href)  # 返回下一页的完整 URL
    else:
        return None


# 定义基础 URL 和请求头
base_url = "https://www.reuters.com/world/china/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# 设置抓取的最大页数和初始变量
max_pages = 2
page_count = 0
current_url = base_url

output_dir = create_output_directory()
news_file = Path(__file__).parent / f"{output_dir}china_news.txt"

# 主循环：抓取新闻页面
while current_url and page_count < max_pages:
    print("正在爬取第", page_count + 1, "页")
    current_url = scrape_page(current_url,news_file)
    page_count += 1
    if current_url and page_count < max_pages:
        time.sleep(5)  # 在请求之间添加 5 秒延迟
