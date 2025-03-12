from rest_framework import serializers
from .models import IbanityAccount

class IbanityAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = IbanityAccount
        fields = [
            'id',
            'account_id',
            'description',
            'product',
            'reference',
            'currency',
            'authorization_expiration_expected_at',
            'current_balance',
            'availableBalance',
            'subtype',
            'holder_name',
            'resourceId'
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'account_id': {'read_only': True},
            'authorization_expiration_expected_at': {'read_only': True}
        }