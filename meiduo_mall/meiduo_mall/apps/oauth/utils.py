import json
import logging
from urllib import parse
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen

from django.conf import settings

from oauth.exceptions import QQAPIException

logger = logging.getLogger('django')


class OAuthQQ(object):
    def __init__(self, app_id=None, app_key=None, redirect_url=None, state=None):
        self.app_id = app_id or settings.QQ_APP_ID
        self.app_key = app_key or settings.QQ_APP_KEY
        self.redirect_url = redirect_url or settings.QQ_REDIRECT_URL
        self.state = state or settings.QQ_STATE

    def generate_qq_login_url(self):
        """
        QQ 登录的链接地址
        :return: QQ登录的链接地址
        """
        url = 'https://graph.qq.com/oauth2.0/authorize?'
        data = {
            "response_type": "code",
            "client_id": self.app_id,
            "redirect_uri": self.redirect_url,
            "state": self.state,
            "scope": "get_user_info"
        }
        query_string = urlencode(data)
        url += query_string
        print(url)
        return url

    def get_access_token(self, code):
        """
        获取QQ的access_code
        :param code: 授权码
        :return: access_code
        """
        url = 'https://graph.qq.com/oauth2.0/token?'
        req_data = {
            "grant_type": "authorization_code",
            "client_id": self.app_id,
            "client_secret": self.app_key,
            "code": code,
            "redirect_uri": self.redirect_url
        }
        url += urlencode(req_data)
        try:
            response = urlopen(url)
            response_data = response.read().decode()
            resp_dict = parse.parse_qs(response_data)
            access_token = resp_dict.get('access_token')[0]
        except Exception as e:
            logger.error(e)
            raise QQAPIException('获取access_token异常')
        return access_token

    def get_openid(self, access_token):
        """
        获取用户的openid
        :param access_token: qq提供的access_token
        :return: open_id
        """
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token
        response = urlopen(url)
        response_data = response.read().decode()
        try:
            # 返回的数据 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            data = json.loads(response_data[10:-4])
        except Exception:
            data = parse_qs(response_data)
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIException('获取openid异常')
        openid = data.get('openid', None)
        return openid


