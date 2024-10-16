from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import scrapy
from datetime import datetime, timedelta
import time
import re
import csv
import os
import random
import subprocess

CONFIG = {
    'CSV_FILE_NAME': 'gold_commodity.csv',
    'CSV_DIR': '/app/scraper/scripts',
    'FIREFOX_BINARY': '/usr/local/firefox/firefox',
    'GECKO_DRIVER_PATH': '/usr/local/bin/geckodriver',
    'START_URLS': ["https://www.reuters.com/site-search/?query=Gold+Commodity/"],
    'CUSTOM_COOKIES': {
        '_lr_geo_location': 'FR',
        'datadome': '~xUKEAVqoV8Vpj4DxbT5bdWhKwv9R0uSOgiZKEEqxSBt5bmhK_kKd5xdBHINIBv4U2ISGREYMsJwTAksmR3ZtTmXFYAuuK8LxFnZCAjXv4DuYdqKT_MZPjjaIQ56D6BF',
        'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Oct+09+2024+13%3A57%3A06+GMT%2B0330+(Iran+Standard+Time)&version=202408.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0c8459c9-fff4-48a4-9ccf-6287d0e4170d&interactionCount=0&isAnonUser=1&landingPath=NotLandingPage&groups=1%3A1%2C3%3A1%2CSSPD_BG%3A1%2C4%3A1%2C2%3A1&AwaitingReconsent=false',
    },
    'USER_AGENTS': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    ]
}


class ReutersSpider(scrapy.Spider):
    name = "reuters"
    allowed_domains = ["reuters.com"]
    start_urls = CONFIG['START_URLS']

    handle_httpstatus_list = [401]

    six_months_ago = datetime.now() - timedelta(days=180)

    custom_cookies = CONFIG['CUSTOM_COOKIES']

    # User-Agent list for random rotation
    user_agents = CONFIG['USER_AGENTS']

    def __init__(self):
        csv_path = os.path.join(CONFIG['CSV_DIR'], CONFIG['CSV_FILE_NAME'])
        print(f"Creating CSV at {csv_path}")
        try:
            self.csv_file = open(csv_path, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(['Title', 'Tags', 'Author', 'Source', 'Content'])
            print("CSV file created and header written.")
        except Exception as e:
            print(f"Error while creating CSV file: {e}")

    def start_requests(self):
        # Request the search page using Selenium for multiple offsets
        for offset in range(0, 41, 20):
            driver = self.start_selenium(offset)

            # Extract links using Selenium
            article_links = self.extract_links(driver)

            # Close Selenium driver after extracting links
            driver.quit()

            # Use Scrapy to process extracted links
            for link in article_links:
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'no-cache',
                    'Referer': 'https://www.reuters.com/'
                }
                yield scrapy.Request(
                    link,
                    headers=headers,
                    cookies=self.custom_cookies,
                    callback=self.parse_article,
                    dont_filter=True
                )

    def start_selenium(self, offset):
        xvfb_command = [
            'xvfb-run', '--auto-servernum', '--server-args', '-screen 0 1024x768x24',
            'geckodriver'
        ]
        xvfb_process = subprocess.Popen(xvfb_command)

        try:
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument('--no-sandbox')
            firefox_options.add_argument('--disable-dev-shm-usage')
            firefox_options.binary_location = CONFIG['FIREFOX_BINARY']

            # Set preferences
            firefox_options.set_preference("network.stricttransportsecurity.preloadlist", False)
            firefox_options.set_preference("security.ssl.enable_ocsp_stapling", False)

            service = Service(CONFIG['GECKO_DRIVER_PATH'])
            driver = webdriver.Firefox(service=service, options=firefox_options)

            search_url = f"https://www.reuters.com/site-search/?query=Gold+Commodity&offset={offset}"
            driver.get(search_url)

            time.sleep(5)
            for cookie_name, cookie_value in self.custom_cookies.items():
                driver.add_cookie({
                    'name': cookie_name,
                    'value': cookie_value,
                    'domain': '.reuters.com'
                })
            driver.get(search_url)
            return driver

        finally:
            xvfb_process.terminate()

    def extract_links(self, driver):
        # Wait for the links to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'body > div > div > div > div > div > div > ul > li > div'))
            )
        except Exception as e:
            self.log(f"Links did not load: {str(e)}")
            return []

        # Extract links from the page
        article_links = driver.find_elements(By.CSS_SELECTOR,
                                             'body > div > div > div > div > div > div > ul > li > div > a')
        links = [link.get_attribute('href') for link in article_links if link.get_attribute('href')]

        self.log(f"Found article links: {links}")
        return links

    def parse_article(self, response):
        # Extract article title
        title = response.css('h1::text').get()

        # Check the publication date and compare with 6 months ago
        pub_date_str = response.css('meta[name="article:published_time"]::attr(content)').get()
        if pub_date_str:
            pub_date = datetime.strptime(pub_date_str.split('T')[0], '%Y-%m-%d')
            if pub_date < self.six_months_ago:
                return  # Ignore articles older than 6 months

        # Extract article content
        paragraphs = response.css('div[data-testid*="paragraph"]::text').getall()
        content = ' '.join(paragraphs)

        # Extract article source
        source = response.css('div.article-body__element__2p5pI p::text').get()

        # Extract authors outside the time tag
        author_elements = response.css(
            'div.info-content__author-date__1Epi_ a::text, div.info-content__author-date__1Epi_ span::text').getall()
        time_authors = response.css('time a::text, time span::text').getall()
        author_cleaned = [author for author in author_elements if author not in time_authors]
        author_text = ', '.join(author_cleaned)
        author_text_clean = re.sub(r"\b(By|and)\b", "", author_text).strip()

        # Extract tag from URL
        url_parts = response.url.split('/')[3:]
        tag = [part for part in url_parts if '-' not in part]

        # Write data to CSV
        self.csv_writer.writerow([title, tag, author_text_clean, source, content])

    def close(self, reason):
        self.csv_file.close()


def run():
    process = CrawlerProcess()
    process.crawl(ReutersSpider)
    process.start()
