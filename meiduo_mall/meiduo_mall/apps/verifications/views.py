from django.shortcuts import render

# Create your views here.

# 引入captcha
# 前端请求接口 users/image_code/<image_code_id>
# 参数image_code_id
# 发送图片给前端
from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.views import APIView

from meiduo_mall.libs.captcha.captcha import captcha
# from libs.captcha.captcha import captcha
from . import constants

class ImageCodeView(APIView):
    """
    图片验证码接口
    1. 生成图片验证码
    2. 将图片验证码编号image_code_id以的形式存入redis， 有效期5分钟
    3. 将图片返回前端
    """
    def get(self, request, image_code_id):
        """图片验证码"""
        # 生成图片验证码
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection("verify_codes")
        redis_conn.setex("IMAGE_CODE_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        return HttpResponse(image, content_type="images/jpg")
