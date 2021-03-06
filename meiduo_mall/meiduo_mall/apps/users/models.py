from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

# Create your models here.
from django.conf import settings

from . import constants


class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

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

    @staticmethod
    def check_send_sms_code_token(token):
        """
        检验access_token
        :param: 待校验的token
        :return: mobile, None
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.SEND_SMS_CODE_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            mobile = data.get('mobile')
            return mobile

    def generate_set_password_token(self):
        """
        生成修改密码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SET_PASSWORD_TOKEN_EXPIRES)
        data = {'user_id': self.id}
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_set_password_token(token, user_id):
        """
        检验设置密码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SET_PASSWORD_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return False
        else:
            if user_id != str(data.get('user_id')):
                return False
            else:
                return True

    def generate_email_verify_url(self):
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.EMAIL_VERIFY_TOKEN_EXPIRES)
        data = {
            'user_id': self.id,
            'email': self.email
        }
        token = serializer.dumps(data)
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token.decode()
        return verify_url

    @staticmethod
    def check_email_verify_token(token):
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.EMAIL_VERIFY_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return False
        else:
            email = data.get('email')
            user_id = data.get('user_id')
            User.objects.filter(id=user_id, email=email).update(email_active=True)
            return True









