from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from ecommerce.serializers.finalize_purchase import CreatePuleSerializer, FinalizePurchaseSerializer
from ecommerce.serializers.download_finalize_purchase import DownloadPurchaseSerializer
from drf_yasg.utils import swagger_auto_schema
from django.core.cache import cache
from ecommerce.models.cart import Cart
from ecommerce.models.wallet import Wallet
import secrets
from django.db import transaction
import json


class FinalizePurchaseAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: FinalizePurchaseSerializer})
    def get(self, request: Request):
        with transaction.atomic():
            cart_json = cache.get(request.user.id)
            cart = Cart(**json.loads(cart_json)) if cart_json else Cart()
            
            if not cart.pules:
                raise ValidationError({"detail": "Carrinho vazio"})
            
            wallet = Wallet.objects.select_for_update().get(user=request.user)
            pules = []
            for pule in cart.pules:
                pule_serializer = CreatePuleSerializer(data=pule.finalize_purchase_payload(), context={"wallet": wallet, "bets": pule.bets})
                pule_serializer.is_valid(raise_exception=True)
                pules.append(pule_serializer.save())

            cart.remove_all()
            cache.set(request.user.id, json.dumps(cart.model_dump(), default=str))
            pdf_id = f"{secrets.token_hex(32)}"
            serializer = FinalizePurchaseSerializer({"pules": pules, "wallet": wallet, "cart": cart.model_dump(), "pdf_id": pdf_id})
            cache_serializer = DownloadPurchaseSerializer(instance={"pules": pules})
            cache.set(f"{pdf_id}.pdf", json.dumps(cache_serializer.data, default=str))
            return Response(data=serializer.data, status=200)
