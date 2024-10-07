# news/filters.py

from django_filters import rest_framework as filters
from .models import News

class NewsFilter(filters.FilterSet):
    keywords = filters.CharFilter(method='filter_keywords', label='Keywords')
    exclude_keyword = filters.CharFilter(method='filter_exclude_keyword', label='Exclude Keyword')

    class Meta:
        model = News
        fields = ['tag']

    def filter_keywords(self, queryset, name, value):
        keywords = value.split()
        for keyword in keywords:
            queryset = queryset.filter(content__icontains=keyword) | queryset.filter(title__icontains=keyword)
        return queryset

    def filter_exclude_keyword(self, queryset, name, value):
        return queryset.exclude(content__icontains=value)
