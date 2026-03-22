from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, GuestOrderTrackingViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'guest-orders', GuestOrderTrackingViewSet, basename='guest-orders')

urlpatterns = router.urls