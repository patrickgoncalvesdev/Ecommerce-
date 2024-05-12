from rest_framework import serializers
from ecommerce.models import Placing


class PlacingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placing
        fields = '__all__'
        