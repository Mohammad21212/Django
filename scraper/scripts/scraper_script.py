import os
import django
import scrapy
from scrapy.crawler import CrawlerProcess
from news_project import settings
from news.models import News

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_django_project.settings')
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
        # استخراج تگ از URL
        tag = response.url.split('/')[-2]

        # یافتن تمام لینک‌های موجود در صفحه
        links = response.css('a::attr(href)').getall()

        # فیلتر کردن لینک‌ها برای استخراج لینک‌های مرتبط با دسته‌بندی
        for link in links:
            if link.startswith('/'):
                link = response.urljoin(link)  # تبدیل لینک‌های نسبی به مطلق

            if link.startswith(response.url):  # فیلتر کردن لینک‌هایی که زیرمجموعه URL اصلی هستند
                yield response.follow(link, self.parse_article, meta={'tag': tag})

        # پیدا کردن لینک صفحه بعدی و ادامه scraping
        next_page = response.css('a.next::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        # استخراج داده‌ها از صفحه مقاله
        tag = response.meta['tag']
        title = response.css('h1::text').get()
        content = ''.join(response.css('p::text').getall())
        source_href = ', '.join(response.css('header > div > div > div > a::attr(href)').getall())
        source_span = ', '.join(response.css('header > div > div > div > a > div > span::text').getall())
        source = f"{source_span} - {source_href}"

        # بررسی اینکه آیا داده‌ها استخراج شده‌اند یا خیر
        if title and content and source:
            # ذخیره داده‌ها در دیتابیس Django
            News.objects.create(
                title=title,
                content=content,
                tag=tag,
                source=source
            )
            self.log(f"Article '{title}' saved to database.")
        else:
            self.log(f"Missing data for {response.url}")

# تنظیمات برای اجرای Scrapy به‌صورت برنامه‌نویسی شده
process = CrawlerProcess(settings={
    'LOG_LEVEL': 'INFO',
})

# اجرای اسپایدر
process.crawl(ZoomitSpider)
process.start()  # اجرا تا زمان پایان اسپایدر متوقف نمی‌شود
