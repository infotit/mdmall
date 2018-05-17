from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer

# Create your models here.
from django.conf import settings

from . import constants


class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def generate_send_sms_code_token(self):
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.SEND_SMS_CODE_TOKEN_EXPIRES)
        data = {
            "mobile": self.mobile
        }

        token = serializer.dumps(data)
        return token.decode()




