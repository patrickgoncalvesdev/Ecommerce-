from rest_framework import serializers
from ecommerce.utils.wallet import truncate


class StatementReportSerializer(serializers.Serializer):
    credit = serializers.DecimalField(max_digits=19, decimal_places=10)
    debit = serializers.DecimalField(max_digits=19, decimal_places=10)
    balance_before = serializers.DecimalField(max_digits=19, decimal_places=10)
    balance_after = serializers.DecimalField(max_digits=19, decimal_places=10)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["balance_before"] = truncate(float(data["balance_before"]), 2)
        data["balance_after"] = truncate(float(data["balance_after"]), 2)
        return data
    
class StatementReportQueryParams(serializers.Serializer):
    date = serializers.DateField(required=True)
    