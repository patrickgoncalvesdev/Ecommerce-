from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from ecommerce.serializers.login import LoginInputSerializer, LoginOutputSerializer
from ecommerce.utils.swagger import Error400, ErrorDetail
from drf_yasg.utils import swagger_auto_schema


class LoginAPIView(APIView):
    @swagger_auto_schema(request_body=LoginInputSerializer, responses={200: LoginOutputSerializer, 400: Error400, 401: ErrorDetail})
    def post(self, request: Request):
        serializer = LoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_serializer = serializer._get_token()
        return Response(token_serializer.data)
