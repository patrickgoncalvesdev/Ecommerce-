from rest_framework import serializers
from ecommerce.models.user import UserAPI
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login
from ecommerce.serializers.user import UserSerializer
from ecommerce.models.verification import Verification
from ecommerce.utils.consts import VerificationType
from ecommerce.serializers.affiliate import AffiliateSerializer


class LoginOutputSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
    affiliate = AffiliateSerializer(allow_null=True, required=False)


class LoginInputSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = UserAPI
        fields = ["username", "password"]

    def _get_object(self) -> UserAPI:
        try:
            user = UserAPI.objects.get(username=self.validated_data["username"])
            if not check_password(self.validated_data["password"], user.password):
                raise AuthenticationFailed
            if not user.is_active and Verification._check_verification(user, VerificationType.REGISTER):
                raise AuthenticationFailed("Verifique o email")
            if not user.is_active:
                raise AuthenticationFailed
            return user
        except UserAPI.DoesNotExist:
            raise AuthenticationFailed

    def _get_token(self) -> LoginOutputSerializer:
        user = self._get_object()
        refresh = RefreshToken.for_user(user)
        update_last_login(None, user)
        serializer = LoginOutputSerializer(
            instance={"access": str(refresh.access_token), "refresh": str(refresh), "user": UserSerializer(instance=user).data, "affiliate": user.affiliate if hasattr(user, "affiliate") else None}
        )
        return serializer
