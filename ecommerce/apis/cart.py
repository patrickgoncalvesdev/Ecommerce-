from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from ecommerce.serializers.create_cart import CreateCartSerializer
from ecommerce.serializers.cart import CartSerializer, PuleSerializer
from drf_yasg.utils import swagger_auto_schema
from django.core.cache import cache
from ecommerce.models.cart import Cart
import json


class CartAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=CreateCartSerializer, responses={200: PuleSerializer})
    def post(self, request: Request):
        serializer = CreateCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pule = serializer.create_pule_cart()
        cart_json = cache.get(request.user.id)
        if not cart_json:
            cart = Cart()
        else:
            cart = Cart(**json.loads(cart_json))
        cart.add_item(pule)
        cache.set(request.user.id, json.dumps(cart.model_dump(), default=str))
        response_serializer = PuleSerializer(instance=pule)
        return Response(data=response_serializer.data, status=200)

    @swagger_auto_schema(responses={200: CartSerializer})
    def get(self, request: Request):
        cart_json = cache.get(request.user.id)
        if not cart_json:
            cart = Cart()
        else:
            cart = Cart(**json.loads(cart_json))
        serializer = CartSerializer(instance=cart)
        return Response(data=serializer.data, status=200)
    
    @swagger_auto_schema(responses={200: CartSerializer})
    def delete(self, request: Request):
        cart = Cart()
        cache.set(request.user.id, json.dumps(cart.model_dump(), default=str))
        serializer = CartSerializer(instance=cart)
        return Response(data=serializer.data, status=200)
    
class CartWithIdAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(responses={200: CartSerializer}, operation_id="delete_item_cart")
    def delete(self, request: Request, id: int):
        cart_json = cache.get(request.user.id)
        if not cart_json:
            cart = Cart()
        else:
            cart = Cart(**json.loads(cart_json))
        cart.remove_item(id)
        cache.set(request.user.id, json.dumps(cart.model_dump(), default=str))
        serializer = CartSerializer(instance=cart)
        return Response(data=serializer.data, status=200)
    