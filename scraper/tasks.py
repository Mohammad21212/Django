from celery import shared_task
from news.models import News
from scrapy.crawler import CrawlerProcess
from scraper.scripts.reuters_spider import ReutersSpider
import os
import csv

@shared_task
def collect_news_task():
    process = CrawlerProcess()
    process.crawl(ReutersSpider)
    process.start()

    csv_file_path = os.path.join(os.path.dirname(__file__), 'gold_commodity_news.csv')

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            News.objects.create(
                title=row['Title'],
                content=row['Content'],
                tag=row['Tags'],
                source=row['Source'],
                authour=row['Authour']
            )
