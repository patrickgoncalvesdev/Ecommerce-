from rest_framework import serializers
from ecommerce.models.affiliate import Affiliate
from ecommerce.models.affiliate_quotation import AffiliateQuotation


class AffiliateQuotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliateQuotation
        fields = ["code", "name"]

class AffiliateSerializer(serializers.ModelSerializer):
    quotations = serializers.SerializerMethodField()
    
    class Meta:
        model = Affiliate
        fields = ["user_above_name", "commission", "quotations"]
        
    def get_quotations(self, obj):
        quotations = AffiliateQuotation.objects.filter(quotation__is_active=True, affiliate=obj)
        return AffiliateQuotationSerializer(quotations, many=True).data
    