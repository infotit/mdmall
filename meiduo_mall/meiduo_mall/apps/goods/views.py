from django.shortcuts import render
from drf_haystack.viewsets import HaystackViewSet
from rest_framework.generics import ListAPIView
from .serializers import SKUSerializer, SKUIndexSerializer
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from rest_framework.filters import OrderingFilter

from .models import SKU
from . import constants
# Create your views here.


class HotSKUListView(ListCacheResponseMixin, ListAPIView):
    # / categories / (?P < category_id >\d +) / hotskus /
    serializer_class = SKUSerializer
    pagination_class = None

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[
               :constants.HOT_SKUS_COUNT_LIMIT - 1]


class SKUListView(ListAPIView):
    serializer_class = SKUSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return SKU.objects.filter(category_id=category_id, is_launched=True)


class SKUSearchViewSet(HaystackViewSet):
    index_models = [SKU]
    serializer_class = SKUIndexSerializer

