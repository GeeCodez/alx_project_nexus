from django.urls import path
from .views import LogoutView, RegisterView, LoginView, MeView, APIRootView, VerifyOTPView, ResendOTPView

urlpatterns = [
    path("", APIRootView.as_view(), name="accounts-root"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path('logout/', LogoutView.as_view(), name='logout'),
]