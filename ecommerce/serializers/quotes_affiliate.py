from rest_framework import serializers
from ecommerce.models.quotation import Quotation
from ecommerce.models.affiliate import Affiliate


class QueryParamsQuotesAffiliateSerializer(serializers.Serializer):
    date = serializers.DateField(required=False)
    quotation = serializers.IntegerField(required=False)
    
    def get_query(self, affiliate: Affiliate):
        payload = self.data
        if payload.get("date"):
            payload["created_at__date"] = payload["date"]
            payload.pop("date")
        if payload.get("quotation"):
            payload["quotation"] = Quotation.objects.get(id=payload["quotation"], affiliates__id=affiliate.id, is_active=True)
        return payload
    
class QuotesAffiliateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Quotation
        fields = ["id", "name"]
        
class QuotesAffiliateReportSerializer(serializers.ModelSerializer):
    sales = serializers.SerializerMethodField()
    commissions = serializers.SerializerMethodField()
    awards = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Affiliate
        fields = ["id", "name", "user_above_name", "sales", "commissions", "awards", "total"]
    
    def get_sales(self, obj):
        query = self.context["query"]
        return obj.sales(query)
    
    def get_commissions(self, obj):
        query = self.context["query"]
        return obj.commissions(query)
    
    def get_awards(self, obj):
        query = self.context["query"]
        return obj.awards(query)
    
    def get_total(self, obj):
        query = self.context["query"]
        return obj.total(query)
    