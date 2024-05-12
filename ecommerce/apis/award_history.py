from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from ecommerce.models.bet import Bet
from drf_yasg.utils import swagger_auto_schema
from ecommerce.serializers.award_history import AwardHistorySerializer


class AwardHistoryAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(responses={200: AwardHistorySerializer(many=True)})
    def get(self, request: Request):
        bets = Bet.objects.filter(win=True).order_by("-draw_date", "-cashout")[:5]
        serializer = AwardHistorySerializer(instance=bets, many=True)
        return Response(serializer.data)
