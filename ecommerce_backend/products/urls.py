from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, PublicAPIView
from django.urls import path, include

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', PublicAPIView.as_view(), name='public-api'),
] + router.urls