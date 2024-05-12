from rest_framework.permissions import BasePermission


class IsAffiliate(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        try:
            return bool(request.user.affiliate and request.user.is_authenticated)
        except:
            return False
        