from django.urls import path
from accounts.views.otp_views import VerifyOTPView, ResendOTPView
from accounts.views.views import APIRootView
from accounts.views.auth_views import (
    LogoutView,
    RegisterView,
    LoginView,
    MeView,
 )
from accounts.views.password_reset_views import (
    PasswordResetRequestView,
    PasswordResetVerifyView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path("", APIRootView.as_view(), name="accounts-root"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("password-reset/request/",PasswordResetRequestView.as_view(),name="password-reset-request"),
    path("password-reset/verify/",PasswordResetVerifyView.as_view(),name="password-reset-verify"),
    path("password-reset/confirm/",PasswordResetConfirmView.as_view(),name="password-reset-confirm",),
]