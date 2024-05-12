from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from ecommerce.utils.swagger import ErrorDetail
from drf_yasg.utils import swagger_auto_schema
from ecommerce.serializers.pule_report import PuleReportSerializer, PuleReportQueryParams
from ecommerce.models.pule import Pule
from drf_yasg import openapi


class PuleReportAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: PuleReportSerializer(many=True), 401: ErrorDetail}, 
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description='Date in YYYY-MM-DD format',
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'hash',
                openapi.IN_QUERY,
                description='Unique hash value',
                type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request: Request):
        query_params = PuleReportQueryParams(data=request.query_params)
        pules = Pule.get_pules(request.user, query_params)
        return Response(PuleReportSerializer(pules, many=True).data)
        