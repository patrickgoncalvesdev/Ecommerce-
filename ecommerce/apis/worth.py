from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from ecommerce.utils.swagger import ErrorDetail
from drf_yasg.utils import swagger_auto_schema
from ecommerce.serializers.modality import ModalitySerializer
from django.core.cache import cache
from ecommerce.models.modality import Modality
from ecommerce.models.cart import Cart
import json


class WorthAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: ModalitySerializer, 401: ErrorDetail}, 
    )
    def get(self, request: Request):
        cart_json = cache.get(request.user.id)
        cart = Cart(**json.loads(cart_json)) if cart_json else Cart()
        print(cart)
        if not cart.pules:
            raise ValidationError({"pules": "Não há pules no carrinho."})
        pule = cart.pules[-1]
        modality = pule.modality
        modalities = Modality.objects.filter(
            min_len_input_guess__lte=modality.min_len_input_guess
        )  
        return Response(ModalitySerializer(modalities, many=True).data)
        