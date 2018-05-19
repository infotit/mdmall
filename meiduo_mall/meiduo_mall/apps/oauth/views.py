from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import OAuthQQUserSerializer

# Create your views here.


# /oauth/qq/authorization/?state=???
# state是指QQ登录后，要跳转的地址
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from oauth.exceptions import QQAPIException
from oauth.models import OAuthQQUser
from .utils import OAuthQQ


class OAuthQQURLView(APIView):
    def get(self, request):
        state = request.query_params.get('state')
        if not state:
            state = '/'

        oauth_qq = OAuthQQ(state=state)
        login_url = oauth_qq.generate_qq_login_url()

        return Response({"oauth_url": login_url})


class OAuthQQUserView(GenericAPIView):
    serializer_class = OAuthQQUserSerializer
    def get(self, request):
        # 获取参数code参数
        code = request.query_params.get('code')
        if not code:
            return Response({"message": "缺少code参数"}, status=status.HTTP_400_BAD_REQUEST)
        # 使用code参数获取access_token
        oauth_qq = OAuthQQ()
        try:
            access_token = oauth_qq.get_access_token(code)
            # 使用access_token获取openid
            openid = oauth_qq.get_openid(access_token)
        except QQAPIException:
            return Response({"message": "获取QQ数据异常"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        # 根据openid查询用户是否在美多绑定过
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 若未绑定，手动创建 绑定需要的access_token，并返回
            access_token = OAuthQQUser.generate_save_user_token(openid)
            return Response({"access_token": access_token})
        else:
            # 若绑定，生成 JWT token，并返回

            # 补充生成记录登录状态的token
            user = oauth_user.user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return Response({
                "token": token,
                "username": user.username,
                "user_id": user.id
            })

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return Response({
            "token": token,
            "username": user.username,
            "user_id": user.id
        })

