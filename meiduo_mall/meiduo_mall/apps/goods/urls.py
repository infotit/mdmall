from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^categories/(?P<category_id>\d+)/hotskus/$', views.HotSKUListView.as_view()),
]
