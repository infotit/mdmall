from rest_framework import serializers

from goods.models import SKU


class CartSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=1)
    selected = serializers.BooleanField(default=True)

    def validate(self, attrs):
        sku_id = attrs['sku_id']
        count = attrs['count']
        selected = attrs['selected']

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        if sku.stock <= count:
            raise serializers.ValidationError('商品库存不足')

        return attrs
