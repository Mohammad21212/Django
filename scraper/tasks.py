from celery import shared_task
from news.models import News
from scrapy.crawler import CrawlerProcess
from scraper.scripts.reuters_spider import ReutersSpider
import os
import csv
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_project.settings')
django.setup()

@shared_task(queue='scrapy_tasks')
def collect_news_task():
    print("Starting the Reuters spider")
    process = CrawlerProcess()
    process.crawl(ReutersSpider)
    process.start()
    print("Finished running the spider")

    csv_file_path = os.path.join('/app/scraper/scripts', 'gold_commodity.csv')
    print(f"Checking for CSV file at {csv_file_path}")

    if os.path.exists(csv_file_path):
        print("CSV file found, reading contents")
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(f"Processing article: {row['Title']}")
                try:
                    News.objects.create(
                        title=row['Title'],
                        content=row['Content'],
                        tag=row['Tags'],
                        source=row['Source'],
                    )
                    print(f"Saved article to database: {row['Title']}")
                except Exception as e:
                    print(f"Error saving article to database: {e}")
    else:
        print("CSV file not found!")

