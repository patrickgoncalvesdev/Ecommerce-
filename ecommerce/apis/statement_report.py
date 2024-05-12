from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from ecommerce.utils.swagger import ErrorDetail
from drf_yasg.utils import swagger_auto_schema
from ecommerce.serializers.statement_report import StatementReportSerializer, StatementReportQueryParams
from ecommerce.models.money_moviment import MoneyMoviment
from drf_yasg import openapi


class StatementReportAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: StatementReportSerializer, 401: ErrorDetail}, 
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description='Date in YYYY-MM-DD format',
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True
            ),
        ]
    )
    def get(self, request: Request):
        query_params = StatementReportQueryParams(data=request.query_params)
        statement = MoneyMoviment.get_grouped_moviment_user_to_report(request.user, query_params)
        return Response(StatementReportSerializer(statement).data)
        