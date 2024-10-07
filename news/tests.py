# news/tests.py

from django.test import TestCase
from rest_framework.test import APIClient
from .models import News

class NewsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        News.objects.create(title='Test News 1', content='This is some test content.', tag='Tech', source='Source 1')
        News.objects.create(title='Test News 2', content='This is another example.', tag='Science', source='Source 2')

    def test_filter_news_by_tag(self):
        response = self.client.get('/api/news/?tag=Tech')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test News 1')
        self.assertNotContains(response, 'Test News 2')

    def test_filter_news_by_keywords(self):
        response = self.client.get('/api/news/?keywords=test content')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test News 1')

    def test_exclude_keyword(self):
        response = self.client.get('/api/news/?exclude_keyword=another')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test News 1')
        self.assertNotContains(response, 'Test News 2')

    def test_combined_filters(self):
        response = self.client.get('/api/news/?keywords=test&exclude_keyword=another')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test News 1')
        self.assertNotContains(response, 'Test News 2')
