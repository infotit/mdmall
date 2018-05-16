import random

from rest_framework import serializers
from django_redis import get_redis_connection


class CheckImageCodeSerializer(serializers.Serializer):
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        redis_conn = get_redis_connection("verify_codes")
        real_image_code = redis_conn.get("IMAGE_CODE_%s" % image_code_id)
        real_image_code = real_image_code.decode()

        if real_image_code is None:
            raise serializers.ValidationError('图片验证码无效')

        redis_conn.delete("IMAGE_CODE_%s" % image_code_id)

        if text.lower() != real_image_code.lower():
            raise serializers.ValidationError('图片验证码输入错误')

        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get('send_flag_%s' % mobile)

        if send_flag:
            raise serializers.ValidationError('发送短信次数过于频繁')

        return attrs

