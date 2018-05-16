import logging
import random

from django.shortcuts import render

# Create your views here.

# 引入captcha
# 前端请求接口 users/image_code/<image_code_id>
# 参数image_code_id
# 发送图片给前端
from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from users.models import User
from . import serializers

from meiduo_mall.libs.captcha.captcha import captcha
# from libs.captcha.captcha import captcha
from . import constants
from meiduo_mall.libs.yuntongxun.sms import CCP
from celery_tasks.sms.tasks import send_sms_code


class ImageCodeView(APIView):
    """
    图片验证码接口
    1. 生成图片验证码
    2. 将图片验证码编号image_code_id以的形式存入redis， 有效期5分钟
    3. 将图片返回前端
    """

    def get(self, request, image_code_id):
        """生成图片验证码，保存图片验证码编号，返回图片"""
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection("verify_codes")
        redis_conn.setex("IMAGE_CODE_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        return HttpResponse(image, content_type="images/jpg")


class SMSCodeView(GenericAPIView):
    serializer_class = serializers.CheckImageCodeSerializer

    def get(self, request, mobile):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 生成验证码
        sms_code = "%06d" % random.randint(0, 999999)
        print('短信验证码是：%s' % sms_code)

        redis_conn = get_redis_connection("verify_codes")
        # redis_conn.setex("SMS_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_conn.setex("send_flag" + mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl = redis_conn.pipeline()
        pl.multi()
        pl.setex("SMS_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()
        # 发送短信验证码

        # ccp = CCP()
        # time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
        # ccp.send_template_sms(mobile, [sms_code, time], constants.SMS_CODE_TEMP_ID)

        # 使用celery发布异步任务
        send_sms_code.delay(mobile, sms_code)

        return Response({"message", "OK"})
