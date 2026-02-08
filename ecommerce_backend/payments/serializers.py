from rest_framework import serializers

class InitializePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()