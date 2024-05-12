from rest_framework import serializers


class DaysReportSerializer(serializers.Serializer):
    days = serializers.ListField(child=serializers.DateField())
    