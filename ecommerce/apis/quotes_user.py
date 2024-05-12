from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from ecommerce.utils.swagger import ErrorDetail
from drf_yasg.utils import swagger_auto_schema
from ecommerce.serializers.quotes_report import QuotesReportSerializer


class QuotesUserDetailReportAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: QuotesReportSerializer, 401: ErrorDetail}, 
    )
    def get(self, request: Request):
        quotation = request.user.quotation
        return Response(QuotesReportSerializer(quotation).data)
    