from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from ecommerce.utils.swagger import ErrorDetail
from drf_yasg.utils import swagger_auto_schema
from ecommerce.serializers.pule_user import PuleUserSerializer, PuleUserQueryParams
from ecommerce.models.pule import Pule


class PulesUserAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: PuleUserSerializer(many=True), 401: ErrorDetail}, 
        query_serializer=PuleUserQueryParams,
    )
    def get(self, request: Request):
        query_params = PuleUserQueryParams(request.query_params)
        pules = Pule.get_pules_to_users(request.user, query_params.data)
        return Response(PuleUserSerializer(pules, many=True).data)
        