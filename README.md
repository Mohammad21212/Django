

# پروژه Tech News

این پروژه شامل چهار چالش اصلی است:

1. **چالش اول**: پیاده‌سازی API اخبار با Django REST Framework
2. **چالش دوم**: جمع‌آوری اخبار از وب‌سایت‌ زومیت با استفاده از Scrapy و ذخیره‌سازی در پایگاه داده Django
3. **چالش سوم**: جمع‌آوری اخبار از وب‌سایت Reuters با استفاده از Scrapy و Selenium و ذخیره‌سازی در فایل CSV
4. **چالش چهارم**: استفاده از Celery برای جمع‌آوری مستمر اخبار و ذخیره در دیتابیس، به همراه Dockerize کردن پروژه

---

## چالش اول: ایجاد API اخبار با Django REST Framework

### مرحله 1: نصب و راه‌اندازی پروژه Django

- ایجاد محیط مجازی Python و نصب Django و Django REST Framework.
- ایجاد پروژه Django با دستور `django-admin startproject`.

### مرحله 2: ایجاد اپلیکیشن News

- ایجاد اپلیکیشن جدید `news` برای مدیریت اخبار و اضافه کردن آن به `INSTALLED_APPS`.
- ایجاد مدل برای اخبار شامل فیلدهای `title`، `content`، `tag` و `source`.

### مرحله 3: ایجاد API با Django REST Framework

- ایجاد Serializer برای مدل News جهت تبدیل داده‌ها به JSON.
- ایجاد View برای API شامل لیست اخبار، فیلتر بر اساس تگ و جستجوی کلمات کلیدی.
- استفاده از `DjangoFilterBackend` برای فیلتر و `SearchFilter` برای جستجو.

### مرحله 4: تست API

- اجرای سرور با دستور `python manage.py runserver` و تست API از طریق Postman یا مرورگر.

---

## چالش دوم: جمع‌آوری اخبار با Scrapy و ذخیره‌سازی در دیتابیس Django

### مرحله 1: نصب و راه‌اندازی Scrapy

- نصب کتابخانه Scrapy و ایجاد اسپایدر Scrapy برای جمع‌آوری اخبار.

### مرحله 2: جمع‌آوری داده‌ها

- تعریف URLهای مختلف برای جمع‌آوری اخبار و استخراج عنوان، محتوا، تگ و منبع.

### مرحله 3: ادغام Scrapy با Django

- تنظیم Scrapy برای ارسال داده‌ها به مدل `News` در Django به‌جای ذخیره در فایل‌های Excel.
- تنظیم Scrapy به عنوان یک اسکریپت اجرایی با استفاده از Django Extensions.

### مرحله 4: اجرای Scrapy و ذخیره داده‌ها در دیتابیس

- اجرای Scrapy با دستور `python manage.py runscript` و جمع‌آوری و ذخیره اخبار در دیتابیس.

---

## چالش سوم: جمع‌آوری اخبار از Reuters با Scrapy و Selenium و ذخیره در CSV

### مرحله 1: نصب و راه‌اندازی Scrapy و Selenium

- نصب Selenium برای تعامل با وب‌سایت‌ها و Scrapy برای پردازش صفحات.

### مرحله 2: اجرای اسکریپت Scrapy و Selenium

- استخراج لینک‌های اخبار با Selenium و پردازش آن‌ها با Scrapy.

### مرحله 3: ذخیره‌سازی داده‌ها در فایل CSV

- ذخیره داده‌های جمع‌آوری شده شامل عنوان، نویسنده، منبع، تگ‌ها و متن در فایل CSV.

### مرحله 4: اجرای اسکریپت از طریق Django

- تنظیم اسکریپت برای اجرا از طریق Django Extensions و ذخیره داده‌ها در فایل `gold_commodity_news.csv`.

---

## چالش چهارم: استفاده از Celery برای جمع‌آوری مستمر اخبار و ذخیره در دیتابیس

### مرحله 1: نصب Celery و Redis

- نصب Celery با دستور `pip install celery`.
- نصب Redis به عنوان Message Broker با دستور `pip install redis`.

### مرحله 2: پیکربندی Celery

- ایجاد فایل `celery.py` در کنار `settings.py` پروژه.
- اضافه کردن Celery به پروژه در فایل `__init__.py` و تنظیمات Celery در `settings.py`.

### مرحله 3: ایجاد تسک Celery برای جمع‌آوری اخبار

- ایجاد تسک Celery در فایل `tasks.py` اپلیکیشن `scraper` برای اجرای مستمر تابع جمع‌آوری اخبار.
- ذخیره داده‌های جمع‌آوری شده از Scrapy در دیتابیس Django.

### مرحله 4: زمان‌بندی جمع‌آوری مستمر با Celery Beat

- تنظیم Celery Beat برای زمان‌بندی تسک‌ها با استفاده از `crontab` برای اجرای تسک جمع‌آوری اخبار هر 30 دقیقه.

### مرحله 5: Dockerize کردن پروژه

- ایجاد فایل `Dockerfile` و `docker-compose.yml` برای مدیریت Django، Celery، Redis و Flower در Docker.
- راه‌اندازی Docker Compose با دستور `docker-compose up --build`.

### مرحله 6: نظارت بر اجرای تسک‌ها با Flower

- نظارت بر اجرای تسک‌ها و صف‌ها با Flower در آدرس `http://localhost:5555`.

---

## نحوه اجرا

### مرحله 1: اجرای API

- اجرای پایگاه داده با دستور `python manage.py migrate`.
- اجرای سرور Django با دستور `python manage.py runserver`.

### مرحله 2: اجرای Scrapy برای چالش دوم

- اجرای Scrapy برای جمع‌آوری اخبار با دستور `python manage.py runscript scraper_script`.

### مرحله 3: اجرای Scrapy و Selenium برای چالش سوم

- اجرای اسکریپت Scrapy و Selenium با دستور `python manage.py runscript reuters_spider`.
- داده‌ها در فایل `gold_commodity_news.csv` ذخیره می‌شوند.

### مرحله 4: اجرای Celery برای جمع‌آوری مستمر اخبار

- راه‌اندازی Celery و Redis با Docker Compose:

  ```bash
  docker-compose up --build
  ```

- نظارت بر تسک‌ها از طریق Flower در آدرس `http://localhost:5555`.

---


---

