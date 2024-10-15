
from django_filters import rest_framework as filters
from .models import News
from django.db.models import Q

class NewsFilter(filters.FilterSet):
    keywords = filters.CharFilter(method='filter_keywords', label='Keywords')
    exclude_keyword = filters.CharFilter(method='filter_exclude_keyword', label='Exclude Keyword')

    class Meta:
        model = News
        fields = ['tag']

    def filter_keywords(self, queryset, name, value):
        keywords = value.split()
        if not keywords:
            return queryset

        query = Q()
        for keyword in keywords:
            query |= Q(content__icontains=keyword) | Q(title__icontains=keyword)

        return queryset.filter(query).distinct()

    def filter_exclude_keyword(self, queryset, name, value):
        return queryset.exclude(content__icontains=value)
