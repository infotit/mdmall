import logging

from django_redis import get_redis_connection
from redis import RedisError
from rest_framework import serializers

logger = logging.getLogger("django")

class CheckImageCodeSerializer(serializers.Serializer):
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        redis_conn = get_redis_connection("verify_codes")
        real_image_code = redis_conn.get("IMAGE_CODE_%s" % image_code_id)

        real_image_code = real_image_code.decode()
        try:
            redis_conn.delete("IMAGE_COD E_%s" % image_code_id)
        except RedisError as e:
            logger.log(e)

        if real_image_code is None:
            raise serializers.ValidationError('无效的图片验证码')
        if text.lower() != real_image_code.lower():
            raise serializers.ValidationError('图片验证码输入错误')

        # get_serializer()时，会对序列化对象添加context属性，是一个字典，包含request, format, view
        # 这三个数据对象，字典形式。只要不是查询字符串或请求体，而是在路径中通过正则表达式提取的参数
        # 一般都放在都在类视图对象的kwargs属性中，
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get('send_flag_' + mobile)

        if send_flag:
            raise serializers.ValidationError('发送短信次数过于频繁')

        return attrs
