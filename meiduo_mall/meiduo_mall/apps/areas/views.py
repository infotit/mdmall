from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Area
from . import serializers


# Create your views here.

class AreaViewSet(ReadOnlyModelViewSet):
    """
    :list: 返回所有省份信息
    :retrieve: 返回省份下属城市信息
    """
    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AreaSerializer
        else:
            return serializers.SubAreaSerializer


