
from rest_framework import serializers

from boloo.shipments.models import Order, Shipment, Transport


class TransportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transport
        fields = (
            'transportId',
            # 'transporterCode', 'trackAndTrace'
        )
        write_only_fields = (
            'transporterCode', 'trackAndTrace'
        )


class OrderSreializer(serializers.ModelSerializer):
    """
        sabhi field serializer me dalane hai aur fir check karna hai return respose and save karte time sara data save hua hai ya nahi 
    """
    class Meta:
        model = Order
        fields = (
            'orderItemId', 'orderId',
            # 'orderDate', 'latestDeliveryDate', 'ean',
            # 'title', 'quantity', 'offerPrice',
            # 'offerCondition', 'fulfilmentMethod'
        )
        write_only_fields = (
            'orderDate', 'latestDeliveryDate', 'ean',
            'title', 'quantity', 'offerPrice',
            'offerCondition', 'fulfilmentMethod'
        )


class SyncShipmentSerializer(serializers.ModelSerializer):
    shipmentItems = OrderSreializer(
        many=True, required=False, source='order_set'
    )
    transport = TransportSerializer()

    class Meta:
        model = Shipment
        fields = (
            'shipmentId', 'shipmentDate', 'shipmentItems', 'transport',
        )

    def create(self, validated_data):
        order = validated_data.pop('order_set', 'shipmentItems')
        transport = validated_data.pop('transport')

        shipment, _ = Shipment.objects.get_or_create(**validated_data)

        for obj in order:
            order, _ = Order.objects.get_or_create(shipment=shipment, **obj)
        transport, _ = Transport.objects.get_or_create(
            shipment=shipment, **transport
        )
        return shipment
