from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import POS


class POSAuthentication(BaseAuthentication):
    """
    Header-based authentication for POS terminal requests.

    The POS must provide X-POS-ID and X-API-KEY headers.
    """

    def authenticate(self, request):
        pos_id = request.headers.get("X-POS-ID")
        api_key = request.headers.get("X-API-KEY")

        if not pos_id or not api_key:
            # Reject requests without the required POS headers.
            raise AuthenticationFailed("Missing POS headers")

        try:
            pos = POS.objects.get(pos_id=pos_id, api_key=api_key)
        except POS.DoesNotExist:
            # Reject invalid POS credentials immediately.
            raise AuthenticationFailed("Invalid POS credentials")

        # Return the authenticated POS instance for use in views.
        return (None, pos)
