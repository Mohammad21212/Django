import os
import sys
import django
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

# Configuration dictionary for settings
CONFIG = {
    'DJANGO_SETTINGS_MODULE': 'news_project.settings',
    'SCRAPY_LOG_LEVEL': 'INFO',
    'START_URLS': [
        'https://www.zoomit.ir/mobile/',
        'https://www.zoomit.ir/laptop/',
        'https://www.zoomit.ir/tablet/',
        'https://www.zoomit.ir/tv/',
        'https://www.zoomit.ir/wearables/',
        'https://www.zoomit.ir/hardware/',
        'https://www.zoomit.ir/tech-iran/',
        'https://www.zoomit.ir/software-application/',
        'https://www.zoomit.ir/os/',
        'https://www.zoomit.ir/internet-network/',
        'https://www.zoomit.ir/gaming/',
        'https://www.zoomit.ir/cryptocurrency/',
    ],
    'SYS_PATH': os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
}

# Add project directory to system path
sys.path.append(CONFIG['SYS_PATH'])

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', CONFIG['DJANGO_SETTINGS_MODULE'])
django.setup()

# Import the Django model after setup
from news.models import News

class ZoomitSpider(scrapy.Spider):
    name = "zoomit"
    start_urls = CONFIG['START_URLS']  # Use URLs from the configuration dictionary

    def parse(self, response):
        tag = response.url.split('/')[-2]  # Extract the tag from the URL
        links = response.css('a::attr(href)').getall()

        # Follow links on the page
        for link in links:
            if link.startswith('/'):
                link = response.urljoin(link)

            if link.startswith(response.url):
                yield response.follow(link, self.parse_article, meta={'tag': tag})

        # Handle pagination by following the next page
        next_page = response.css('a.next::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        tag = response.meta['tag']
        title = response.css('h1::text').get()
        content = ''.join(response.css('p::text').getall())
        source_href = ', '.join(response.css('header > div > div > div > a::attr(href)').getall())
        source_span = ', '.join(response.css('header > div > div > div > a > div > span::text').getall())
        source = f"{source_span} - {source_href}"

        # Save article to the database if all data is present
        if title and content and source:
            News.objects.create(
                title=title,
                content=content,
                tag=tag,
                source=source
            )
            self.log(f"Article '{title}' saved to database.")
        else:
            self.log(f"Missing data for {response.url}")

# Configure Scrapy logging
configure_logging({'LOG_LEVEL': CONFIG['SCRAPY_LOG_LEVEL']})

# Create and run the Scrapy crawler
runner = CrawlerRunner(settings={
    'LOG_LEVEL': CONFIG['SCRAPY_LOG_LEVEL'],
})

d = runner.crawl(ZoomitSpider)
d.addBoth(lambda _: reactor.stop())
reactor.run()
