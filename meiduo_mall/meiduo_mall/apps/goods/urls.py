from django.conf.urls import url
from rest_framework import routers

from . import views

urlpatterns = [
    url(r'^categories/(?P<category_id>\d+)/hotskus/$', views.HotSKUListView.as_view()),
    url(r'^categories/(?P<category_id>\d+)/skus/$', views.SKUListView.as_view()),
]

router = routers.DefaultRouter()
router.register('skus/search', views.SKUSearchViewSet, base_name='skus-search')
urlpatterns += router.urls
