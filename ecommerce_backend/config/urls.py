from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)
from rest_framework import permissions
from .views import APIRootView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path('api/orders/', include('orders.urls')),
    path("api/payments/", include("payments.urls")),
    path("api/accounts/", include("accounts.urls")),
    path('api/products/', include('products.urls')),
    
    path("", APIRootView.as_view(), name="api-root"),
]