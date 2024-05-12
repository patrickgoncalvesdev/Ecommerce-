from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from ecommerce.models.user import UserAPI


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
            return UserAPI.objects.get(pk=user_id)
        except UserAPI.DoesNotExist:
            return None
