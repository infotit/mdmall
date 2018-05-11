from django.conf.urls import url

# 前端请求接口 users/image_code/<image_code_id>
from . import views

urlpatterns = [
    url(r'^image_codes/(?P<image_code_id>.+)/$', views.ImageCodeView.as_view()),
]
