from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from ecommerce.serializers.perfil import PerfilSerializer, PerfilUpdateSerializer
from ecommerce.utils.swagger import Error400
from drf_yasg.utils import swagger_auto_schema
from ecommerce.models.verification import Verification
from ecommerce.utils.consts import VerificationType
from django.db import transaction


class PerfilAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: PerfilSerializer})
    def get(self, request: Request):
        serializer = PerfilSerializer(instance=request.user)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=PerfilUpdateSerializer, responses={200: PerfilSerializer, 400: Error400})
    def patch(self, request: Request):
        if Verification._check_verification(request.user, VerificationType.UPDATE_PERFIL):
            raise ValidationError({"detail": "Aguarde a confirmação do email"})
        serializer = PerfilUpdateSerializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            Verification._desactive_others_verifications(request.user, VerificationType.UPDATE_PERFIL)
            Verification.objects.create(user=request.user, type=VerificationType.UPDATE_PERFIL, data=serializer.validated_data)
        return Response(PerfilSerializer(request.user).data)
    