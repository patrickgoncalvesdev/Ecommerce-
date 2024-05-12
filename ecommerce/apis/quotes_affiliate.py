from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from ecommerce.utils.permissions import IsAffiliate
from ecommerce.utils.swagger import ErrorDetail
from drf_yasg.utils import swagger_auto_schema
from ecommerce.serializers.quotes_affiliate import QuotesAffiliateSerializer, QuotesAffiliateReportSerializer, QueryParamsQuotesAffiliateSerializer
from ecommerce.models.quotation import Quotation
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from ecommerce.utils.pdf import CreatePDF, AffiliateReport


class QuotesAffiliateAPI(APIView):
    permission_classes = [IsAffiliate]

    @swagger_auto_schema(
        responses={200: QuotesAffiliateSerializer, 401: ErrorDetail}, 
    )
    def get(self, request: Request):
        quotations = request.user.affiliate.quotations.filter(is_active=True)
        return Response(QuotesAffiliateSerializer(quotations, many=True).data)
        
class QuotesAffiliateReportAPI(APIView):
    permission_classes = [IsAffiliate]

    @swagger_auto_schema(
        responses={200: QuotesAffiliateReportSerializer, 401: ErrorDetail, 404: ErrorDetail}, 
        query_serializer=QueryParamsQuotesAffiliateSerializer
    )
    def get(self, request: Request):
        try:
            query_serializer = QueryParamsQuotesAffiliateSerializer(request.query_params)
            query = query_serializer.get_query(request.user.affiliate)
            return Response(QuotesAffiliateReportSerializer(request.user.affiliate, context={"query": query}).data)
        except Quotation.DoesNotExist:
            return Response({"detail": "Cotação ativa não encontrada."}, status=404)
        
class DownloadQuotesAffiliateReportAPI(APIView):
    permission_classes = [IsAffiliate]

    @swagger_auto_schema(
        responses={200: QuotesAffiliateReportSerializer, 401: ErrorDetail, 404: ErrorDetail},
        query_serializer=QueryParamsQuotesAffiliateSerializer 
    )
    def get(self, request: Request):
        try:
            query_serializer = QueryParamsQuotesAffiliateSerializer(request.query_params)
            query = query_serializer.get_query(request.user.affiliate)
            payload = QuotesAffiliateReportSerializer(request.user.affiliate, context={"query": query}).data
            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="relatorio_afiliado.pdf"'
            pdf = canvas.Canvas(response, pagesize=letter)
            creator_pdf = CreatePDF(pdf)
            report = AffiliateReport(**payload, query=query)
            creator_pdf.create_affiliate_report(report)
            return response
        except Quotation.DoesNotExist:
            return Response({"detail": "Cotação ativa não encontrada."}, status=404)
        