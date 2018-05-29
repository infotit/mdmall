import re

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.views import ObtainJSONWebToken

from goods.models import SKU
from goods.serializers import SKUSerializer
from users.serializers import EmailSerializer
from .models import User
from .serializers import UserDetailSerializer
from verifications.serializers import CheckImageCodeSerializer
from . import serializers
from .utils import get_user_by_account
from . import constants
from carts.utils import merge_cookie_to_redis


class UsernameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            "username": username,
            "count": count
        }
        return Response(data)


class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            "mobile": mobile,
            "count": count
        }
        return Response(data)


class UserView(CreateAPIView):
    """
    用户注册
    """
    serializer_class = serializers.CreateUserSerializer


class SMSCodeTokenView(GenericAPIView):
    serializer_class = CheckImageCodeSerializer

    def get(self, request, account):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = get_user_by_account(account)
        if user is None:
            return Response({"message": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        mobile = re.sub(r'^(\d{3})\d{4}(\d{4})$', r'\1****\2', user.mobile)
        access_token = user.generate_send_sms_code_token()
        return Response({
            'mobile': mobile,
            'access_token': access_token
        })


class PasswordTokenView(GenericAPIView):
    """
    用户帐号设置密码的token
    """
    serializer_class = serializers.CheckSMSCodeSerializer

    def get(self, request, account):
        """
        根据用户帐号获取修改密码的token
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        # 生成修改用户密码的access token
        access_token = user.generate_set_password_token()

        return Response({'user_id': user.id, 'access_token': access_token})


class PasswordView(mixins.UpdateModelMixin, GenericAPIView):
    """
    用户密码
    """
    queryset = User.objects.all()
    serializer_class = serializers.ResetPasswordSerializer

    def post(self, request, pk):
        return self.update(request, pk)


class UserDetailView(RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    """
    用户邮箱
    """
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmailVerifyView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({"message": "缺少token"}, status=status.HTTP_400_BAD_REQUEST)
        result = User.check_email_verify_token(token)
        if result:
            return Response({"message": "OK"})
        else:
            return Response({"message": "非法的token"}, status=status.HTTP_400_BAD_REQUEST)


class UserHistoryView(mixins.CreateModelMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AddUserHistorySerializer

    def post(self, request):
        return self.create(request)

    def get(self, request):
        user_id = request.user.id
        # 从redis中查询数据
        redis_conn = get_redis_connection("history")
        sku_ids_list = redis_conn.lrange("history_%s" % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT)

        # 根据redis查询的编号，从数据库中查询数据
        sku_list = []
        for sku_id in sku_ids_list:
            sku_obj = SKU.objects.get(id=sku_id)
            sku_list.append(sku_obj)
        # 利用序列化器序列化数据
        serializer = SKUSerializer(sku_list, many=True)
        # 返回数据
        return Response(serializer.data)


class UserAuthenticationView(ObtainJSONWebToken):
    def post(self, request):
        response = super().post(request)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            response = merge_cookie_to_redis(request, response, user)
        return response