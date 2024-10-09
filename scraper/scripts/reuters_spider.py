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


class ReutersSpider(scrapy.Spider):
    name = "reuters"
    allowed_domains = ["reuters.com"]
    start_urls = ["https://www.reuters.com/site-search/?query=Gold+Commodity"]

    # Calculate the date 6 months ago
    six_months_ago = datetime.now() - timedelta(days=180)

    # Custom cookies including datadome and other cookies
    custom_cookies = {
        '_lr_geo_location': 'FR',
        'datadome': '~xUKEAVqoV8Vpj4DxbT5bdWhKwv9R0uSOgiZKEEqxSBt5bmhK_kKd5xdBHINIBv4U2ISGREYMsJwTAksmR3ZtTmXFYAuuK8LxFnZCAjXv4DuYdqKT_MZPjjaIQ56D6BF',
        'OptanonConsent': 'isGpcEnabled=0&datestamp=Tue+Oct+08+2024+20%3A54%3A21+GMT%2B0330+(Iran+Standard+Time)&version=202408.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0c8459c9-fff4-48a4-9ccf-6287d0e4170d&interactionCount=0&isAnonUser=1&landingPath=https%3A%2F%2Fwww.reuters.com%2Fsite-search%2F%3Fquery%3DGold+Commodity&groups=1%3A1%2C3%3A1%2CSSPD_BG%3A1%2C4%3A1%2C2%3A1',
        'reuters-geo': '{"country":"-","region":"-"}'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.reuters.com/'
    }

    def __init__(self):
        # Set the path for CSV file inside the scripts folder
        csv_path = os.path.join(os.path.dirname(__file__), 'gold_commodity_news.csv')

        # Create or open the CSV file for writing
        self.csv_file = open(csv_path, 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)

        # Write the header row to CSV
        self.csv_writer.writerow(['Title', 'Tags', 'Author', 'Source', 'News Text'])

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
                yield scrapy.Request(link, headers=self.headers, cookies=self.custom_cookies,
                                     callback=self.parse_article)

    def start_selenium(self, offset):
        # Initialize Selenium with Firefox
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.binary_location = r'C:\Users\moham\AppData\Local\Mozilla Firefox\firefox.exe'
        firefox_options.set_preference("network.stricttransportsecurity.preloadlist", False)
        firefox_options.set_preference("security.ssl.enable_ocsp_stapling", False)

        service = Service('D:\setup\geckodriver-v0.35.0-win32\geckodriver.exe')
        driver = webdriver.Firefox(service=service, options=firefox_options)

        # Go to the Reuters search page with the specified offset
        search_url = f"https://www.reuters.com/site-search/?query=Gold+Commodity&offset={offset}"
        driver.get(search_url)

        # Add cookies
        for cookie_name, cookie_value in self.custom_cookies.items():
            driver.add_cookie({
                'name': cookie_name,
                'value': cookie_value,
                'domain': '.reuters.com'
            })

        # Reload the page after adding cookies
        driver.get(search_url)

        return driver

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
        news_text = ' '.join(paragraphs)

        # Extract article source
        source = response.css('div.article-body__element__2p5pI p::text').get()

        # Extract authors outside the time tag
        author_elements = response.css(
            'div.info-content__author-date__1Epi_ a::text, div.info-content__author-date__1Epi_ span::text').getall()
        time_authors = response.css('time a::text, time span::text').getall()
        author_cleaned = [author for author in author_elements if author not in time_authors]
        author_text = ', '.join(author_cleaned)
        author_text_clean = re.sub(r"\b(By|and)\b", "", author_text).strip()

        # Extract tags from URL
        url_parts = response.url.split('/')[3:]
        tags = [part for part in url_parts if '-' not in part]

        # Write data to CSV
        self.csv_writer.writerow([title, tags, author_text_clean, source, news_text])

    def close(self, reason):
        # Close the CSV file when the spider finishes
        self.csv_file.close()


def run():
    process = CrawlerProcess()
    process.crawl(ReutersSpider)
    process.start()
