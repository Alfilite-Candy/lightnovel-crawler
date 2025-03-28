from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import random
import time
import re

#处理爬取到的HTML文本
def process_text(html_content):
    processed = re.sub(r'(?i)</\s*p\s*>', '\n', html_content)
    processed = re.sub(r'<[^>]+>', '', processed)
    processed = re.sub(r'\n+', '\n', processed).strip()
    return processed

#处理文件名中的特殊字符
def sanitize_filename(filename):
    # 替换Windows文件系统不允许的字符
    invalid_chars = r'[\\/:*?"<>|]'
    # 替换为下划线
    sanitized = re.sub(invalid_chars, '_', filename)
    # 移除前后的空白字符
    sanitized = sanitized.strip()
    return sanitized

#输入小说的目录页网址
URL = input("请输入小说的目录页网址(多个网址请用空格分隔):")
urls = [url.strip() for url in URL.split()]

#驱动配置
driver_file_path = 'msedgedriver.exe'
service = Service(driver_file_path)
options = Options()
driver = webdriver.Edge(service=service, options=options)


for url in urls:
    driver.get(url)
    #爬取标题
    book_title_xpath = '/html/body/div[2]/div[3]/div[1]/h1'
    book_title = driver.find_element(By.XPATH, book_title_xpath).text
    #处理文件名中的特殊字符
    safe_title = sanitize_filename(book_title)
    #没有可爬取内容时结束任务
    try:
        with open('novel/' + safe_title + '.txt', "w+", encoding='utf-8') as f:
            #进入轻小说开始页
            first_part_xpath = '/html/body/div[2]/div[3]/div[2]/div[2]/div/ul/li[1]/a'
            begin_button = driver.find_element(By.XPATH, first_part_xpath)
            begin_button.click()
            time.sleep(2)
            #开始爬取每页内容
            while True:
                #爬取章节标题
                part_title_xpath = '//*[@id="mlfy_main_text"]/h1'
                part_title = driver.find_element(By.XPATH, part_title_xpath).text
                f.write('\n' + part_title + '\n\n')
                #爬取章节内容
                article_xpath='//*[@id="TextContent"]'
                article=driver.find_element(By.XPATH,article_xpath).text
                f.write(process_text(article))
                #进入下一页
                next_part_xpath = '//*[@id="readbg"]/p/a[5]'
                button = driver.find_element(By.XPATH, next_part_xpath)
                #随机等待,反爬虫
                time.sleep(random.randint(0, 2))
                button.click()
                time.sleep(1)
    except NoSuchElementException:
        pass
#退出驱动
driver.quit()