from django.conf.urls import url
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register('areas', views.AreaViewSet, base_name='area')

urlpatterns = [

]

urlpatterns += router.urls
