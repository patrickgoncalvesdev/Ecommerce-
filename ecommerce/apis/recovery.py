from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from ecommerce.models.user import UserAPI
from ecommerce.serializers.recovery import RecoveryPasswordSerializer
from ecommerce.utils.swagger import Error400
from drf_yasg.utils import swagger_auto_schema
from ecommerce.models.verification import Verification
from ecommerce.utils.consts import VerificationType
from django.db import transaction


class RecoveryPasswordAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RecoveryPasswordSerializer, responses={200: RecoveryPasswordSerializer, 400: Error400})
    def post(self, request: Request):
        serializer = RecoveryPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserAPI.objects.filter(username=serializer.validated_data["username"], is_active=True).first()
        if not user:
            raise ValidationError({"username": "Usuário não encontrado"})
        if Verification._check_verification(user, VerificationType.RECOVERY_PASSWORD):
            raise ValidationError({"detail": "Aguarde a confirmação do email/sms"})
        with transaction.atomic():
            Verification._desactive_others_verifications(user, VerificationType.RECOVERY_PASSWORD)
            Verification.objects.create(user=user, type=VerificationType.RECOVERY_PASSWORD, data=serializer.validated_data)
        return Response(serializer.data)
    