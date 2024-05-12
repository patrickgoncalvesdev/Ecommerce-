from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from ecommerce.serializers.active_verification import ActiveVerificationSerializer
from ecommerce.models.verification import Verification
from ecommerce.models.user import UserAPI
from ecommerce.utils.swagger import ErrorDetail
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone
from django.db import transaction


class VerificationAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(responses={200: ActiveVerificationSerializer, 401: ErrorDetail})
    def get(self, request: Request, token: str):
        try:
            with transaction.atomic():
                verification = Verification.objects.get(token=token, expires_at__gte=timezone.now(), actived=False)
                verification.actived = True
                UserAPI.objects.filter(id=verification.user.pk).update(**verification.data)
                verification.save()
                return Response(ActiveVerificationSerializer(verification).data)
        except Verification.DoesNotExist:
            return Response({"detail": "Token inválido"}, status=401)
        