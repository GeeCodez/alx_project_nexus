from django.urls import path
from .views import RegisterView, LoginView, MeView, APIRootView

urlpatterns = [
    path("accounts/", APIRootView.as_view(), name="accounts-root"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
]