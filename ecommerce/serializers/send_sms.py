from rest_framework import serializers


class SendSmsSerializers(serializers.Serializer):
    number = serializers.CharField()
    message = serializers.CharField()
