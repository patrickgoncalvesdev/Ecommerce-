from rest_framework import serializers
from ecommerce.models.quotation_modality import QuotationModality
from ecommerce.models.quotation import Quotation


class QuotationModalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationModality
        fields = ["modality_name", "placing_name", "multiplier"]


class QuotesReportSerializer(serializers.ModelSerializer):
    quotations = serializers.SerializerMethodField()
    
    class Meta:
        model = Quotation
        fields = ["name", "quotations"]
        
    def get_quotations(self, obj):
        queryset = obj.quotation_modalities.all().distinct("modality")
        return QuotationModalitySerializer(queryset, many=True).data
        