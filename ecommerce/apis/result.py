from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from ecommerce.utils.swagger import ErrorDetail
from drf_yasg.utils import swagger_auto_schema
from ecommerce.models.lottery import Lottery
from ecommerce.serializers.lottery_by_results import ResultSerializer


class ResultAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: ResultSerializer(many=True), 401: ErrorDetail}, 
    )
    def get(self, request: Request):
        lotteries = Lottery.get_lotteries_active()
        return Response(ResultSerializer(lotteries, many=True).data)
        