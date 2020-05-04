from django.conf import settings
from rest_framework import serializers

from boloo.accounts.models import Seller


class SellerSerializer(serializers.ModelSerializer):
    """
    Serializer for seller
    """

    class Meta:
        model = Seller

        fields = (
            'seller_name',
            'seller_code',
            'email',
            'client_id',
            'client_secret_key',
        )

        read_only_fields = (
            'seller_code',
            'client_id',
            'client_secret_key',
            'access_token',
        )

        def create(self, validated_data):
            return Seller(**validated_data)


class TokenSerializer(serializers.Serializer):
    """ serializer for token related things."""

    access_token = serializers.CharField(
        max_length=256, min_length=8, read_only=True
    )
    token_type = serializers.CharField(
        max_length=20, default=None, allow_null=True, read_only=True
    )
    expires_in = serializers.IntegerField(
        required=False, default=None, allow_null=True, read_only=True
    )
    scope = serializers.CharField(
        max_length=20, default=None, allow_null=True, read_only=True
    )
    client_id = serializers.CharField(
        max_length=128, default=None, allow_null=True,
    )
    client_secret_key = serializers.CharField(
        max_length=256, default=None, allow_null=True,
    )

    class Meta:
        fields = (
            'access_token',
            'token_type',
            'expires_in',
            'scope',
        )
        exclude = (
            'client_id',
            'client_secret_key'
        )

    def validate(self, data):
        """
            Check the valid credentials
        """
        try:
            seller = Seller.objects.get(
                client_id=data['client_id'],
                client_secret_key=data['client_secret_key']
            )
            return {
                'access_token': seller.refresh_access_token(),
                'token_type': 'Bearer',
                'expires_in': settings.ACCESS_TOKEN_EXPIRES,
                'scope': 'RETAILER'
            }
        except Seller.DoesNotExist:
            raise serializers.ValidationError(
                'Invalid Credentials'
            )
        return data
