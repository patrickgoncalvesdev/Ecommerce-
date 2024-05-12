from rest_framework import serializers


class SendEmailSerializers(serializers.Serializer):
    to = serializers.EmailField()
    subject = serializers.CharField()
    body = serializers.CharField()
    