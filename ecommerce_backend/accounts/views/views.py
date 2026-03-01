from rest_framework import generics, permissions
from rest_framework.response import Response

class APIRootView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({
            "register": request.build_absolute_uri("/api/accounts/register/"),
            "login": request.build_absolute_uri("/api/accounts/login/"),
            "me": request.build_absolute_uri("/api/accounts/me/"),
        })
