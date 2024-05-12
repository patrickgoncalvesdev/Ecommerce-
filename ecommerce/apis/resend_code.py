from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from ecommerce.serializers.resend_code import ResendCodeInputSerializer
from ecommerce.models.verification import Verification
from ecommerce.utils.consts import VerificationType
from ecommerce.utils.swagger import ErrorDetail, SendEmailSerializer, Error400
from ecommerce.utils.mail import get_register_message
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone
from django.conf import settings
from django.db import transaction


class ResendCodeRegisterAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=ResendCodeInputSerializer, responses={200: SendEmailSerializer, 400: Error400, 401: ErrorDetail})
    def post(self, request: Request):
        with transaction.atomic():
            serializer = ResendCodeInputSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            if Verification.objects.filter(user__email=serializer.validated_data["email"], actived=True, type=VerificationType.REGISTER).exists():
                return Response({"detail": "Usuário já verificado"}, status=400)
            
            old_verification = Verification.objects.filter(user__email=serializer.validated_data["email"], type=VerificationType.REGISTER, resend_expires_at__gt=timezone.now()).first()
            if old_verification:
                wait = old_verification.resend_expires_at - timezone.now()
                return Response({"detail": f"Você já solicitou um código, aguarde {wait.seconds}"}, status=400)
            Verification._desactive_others_verifications(serializer.instance, VerificationType.REGISTER)
            verification = Verification.objects.create(user=serializer.instance, type=VerificationType.REGISTER, data={"is_active": True}, resend_expires_at=timezone.now() + timezone.timedelta(minutes=1))
            title, text = get_register_message(serializer.validated_data["email"], verification.token)
            settings.MAIL_REPOSITORY.execute_async(
                to=serializer.validated_data["email"],
                subject=title,
                body=text,
            )
            output_serializer = SendEmailSerializer(instance={"message": "Email enviado com sucesso"})
            return Response(output_serializer.data)
    