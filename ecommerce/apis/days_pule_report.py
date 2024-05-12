from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from ecommerce.utils.swagger import ErrorDetail
from drf_yasg.utils import swagger_auto_schema
from ecommerce.serializers.days_pules_report import DaysReportSerializer
from ecommerce.models.pule import Pule


class DaysPuleReportAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: DaysReportSerializer, 401: ErrorDetail}, 
    )
    def get(self, request: Request):
        pules = Pule.get_days_pule_user(request.user)
        data = {"days": pules}
        return Response(DaysReportSerializer(data).data)
        