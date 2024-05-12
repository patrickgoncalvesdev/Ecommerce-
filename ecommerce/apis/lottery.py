from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from ecommerce.serializers.lottery import LotterySerializer
from ecommerce.models import Lottery
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone


class LotteryAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: LotterySerializer(many=True)})
    def get(self, request: Request):
        current_timezone = timezone.get_current_timezone()
        now = timezone.now().astimezone(current_timezone)
        now_sum_1_hour = now + timezone.timedelta(hours=1)
        lotteries = Lottery.objects.filter(is_active=True, draws__date__gt=now_sum_1_hour, draws__is_active=True).distinct()
        serializer = LotterySerializer(instance=lotteries, many=True)
        return Response(serializer.data)
