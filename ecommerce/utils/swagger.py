from rest_framework import serializers


class Error400(serializers.Serializer):
    field = serializers.ListField(child=serializers.CharField(), required=False)
    detail = serializers.CharField(required=False)
    
class ErrorDetail(serializers.Serializer):
    detail = serializers.CharField()

class SendEmailSerializer(serializers.Serializer):
    message = serializers.CharField()
    