from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from ecommerce.serializers.register import RegisterSerializer, RegisterOutPutSerializer
from ecommerce.utils.swagger import Error400
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction
import logging


# TODO AJustar validação de erro


class RegisterAPI(APIView):
    permission_classes = [AllowAny]
    logger = logging.getLogger(__name__)

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request: Request):
        try:
            with transaction.atomic():
                serializer = RegisterSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(
                    RegisterOutPutSerializer(serializer.instance).data, status=201
                )  # TODO REMOVER ISSO
        except Exception as e:
            self.logger.error(f"Error on register: {e}")
            if not isinstance(e, ValidationError):
                return Response({"detail": str(e)}, status=400)
            raise e
