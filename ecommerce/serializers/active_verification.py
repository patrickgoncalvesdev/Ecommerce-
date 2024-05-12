from rest_framework import serializers
from ecommerce.models.verification import Verification


class ActiveVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = "__all__"
        