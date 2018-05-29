import base64

import pickle
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from .serializers import CartSerializer, CartSKUSerializer, CartDeleteSerializer


class CartView(APIView):
    # 重写perform_authentication方法

    def perform_authentication(self, request):
        pass

    def post(self, request):
        # 校验前端数据
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            # 登录 保存数据到redis
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('cart_select_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # 未登录 保存数据到cookie

            # 读取用户cookie
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            if sku_id in cart_dict:
                cart_count = cart_dict[sku_id]['count']
                count += cart_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            response.set_cookie('cart', cart_cookie)
            return response

    def get(self, request):
        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            # 登录 从redis中查询数据
            redis_conn = get_redis_connection('cart')
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)
            cart_selected = redis_conn.smembers('cart_select_%s' % user.id)
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }
        else:
            # 未登录 从cookie中查询数据
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        # 数据库中查询商品数据
        sku_id_list = cart_dict.keys()
        sku_obj_list = SKU.objects.filter(id__in=sku_id_list)

        # 补充查询集中缺少的数据，count，selected
        for sku in sku_obj_list:
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']

        # 返回数据给前端
        serializer = CartSKUSerializer(sku_obj_list, many=True)
        return Response(serializer.data)

    def put(self, request):
        # 校验前端数据
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hset('cart_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('cart_select_%s' % user.id, sku_id)
            else:
                pl.srem('cart_select_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data)

        else:
            # 未登录 从cookie中查询数据
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            if sku_id in cart_dict:
                cart_dict[sku_id] = {
                    'count': count,
                    'selected': selected
                }
            cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response = Response(serializer.data)
            response.set_cookie('cart', cart_cookie)
            return response

    def delete(self, request):
        # 校验数据
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')

        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            # 登录 删除redis中数据
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id, sku_id)
            pl.srem('cart_select_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        else:
            # 未登录 删除cookie中数据
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        response = Response(data=serializer.data)
        if sku_id in cart_dict:
            del cart_dict[sku_id]
            cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('cart', cart_cookie)
        return response
