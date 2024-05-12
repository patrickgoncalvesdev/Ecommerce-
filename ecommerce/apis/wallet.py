from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from ecommerce.models.user import UserAPI
from ecommerce.serializers.wallet import WalletSerializer
from drf_yasg.utils import swagger_auto_schema


class WalletDataAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: WalletSerializer})
    def get(self, request: Request):
        user = UserAPI.objects.get(username=request.user.username)
        serializer = WalletSerializer(instance=user.wallet)
        return Response(serializer.data)
