import base64
import pickle

from django_redis import get_redis_connection


def merge_cookie_to_redis(request, response, user):
    # 取出cookie购物车数据
    cart_str = request.COOKIES.get('cart')
    if not cart_str:
        return response
    cart_cookie_dict = pickle.loads(base64.b64decode(cart_str.encode()))
    # 取出redis购物车数据
    redis_conn = get_redis_connection('cart')
    redis_dict = redis_conn.hgetall('cart_%s' % user.id)

    # cookie中的购物车数据结构
    # {
    #     sku_id: {
    #                 "count": xxx, // 数量
    #     "selected": True // 是否勾选
    # },
    # sku_id: {
    #     "count": xxx,
    #     "selected": False
    # },
    # ...
    # }

    cart = {}
    # 将redis中购物车数据转换成int
    for sku_id, count in redis_dict.items():
        cart[int(sku_id)] = int(count)

    selected_list = []
    for sku_id, selected_count_dict in cart_cookie_dict.items():
        cart[sku_id] = selected_count_dict['count']
        if selected_count_dict['selected']:
            selected_list.append(sku_id)
    pl = redis_conn.pipeline()

    # 将cookie和redis数据合并
    pl.hmset('cart_%s' % user.id, cart)
    if len(selected_list) > 0:
        pl.sadd('cart_select_%s' % user.id, *selected_list)
    pl.execute()

    # 清除cookie中购物车数据
    response.delete_cookie('cart')
    return response
