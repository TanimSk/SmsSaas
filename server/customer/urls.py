from django.urls import path
from customer.views import (
    ConsumerRegistrationView,
    CustomerProfileView,
)
from administrator.auth_view import VerifyOTP

urlpatterns = [
    path(
        "registration/",
        ConsumerRegistrationView.as_view(),
        name="registration_customer",
    ),
    path(
        "verify-otp/",
        VerifyOTP.as_view(),
        name="verify_otp",
    ),
    path(
        "profile/",
        CustomerProfileView.as_view(),
        name="customer_profile",
    ),
]
