from django.conf.urls import url

from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^users/$', views.UserView.as_view()),
    url(r'usernames/(?P<username>\w{5,20})/count/', views.UsernameCountView.as_view()),
    url(r'mobiles/(?P<mobile>1[345789]\d{9})/count/', views.MobileCountView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
]


