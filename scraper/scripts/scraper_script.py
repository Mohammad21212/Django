import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

from news.models import News

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_project.settings')
django.setup()

class ZoomitSpider(scrapy.Spider):
    name = "zoomit"
    start_urls = [
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
    ]

    def parse(self, response):
        tag = response.url.split('/')[-2]
        links = response.css('a::attr(href)').getall()

        for link in links:
            if link.startswith('/'):
                link = response.urljoin(link)

            if link.startswith(response.url):
                yield response.follow(link, self.parse_article, meta={'tag': tag})

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

configure_logging()
runner = CrawlerRunner(settings={
    'LOG_LEVEL': 'INFO',
})

d = runner.crawl(ZoomitSpider)
d.addBoth(lambda _: reactor.stop())
reactor.run()