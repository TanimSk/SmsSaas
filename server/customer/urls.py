from django.urls import path
from customer.views import ConsumerRegistrationView, CustomerProfileView, APIKeyView, SMSView
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
    path(
        "api-key/",
        APIKeyView.as_view(),
        name="api_key",
    ),
    path(
        "all-sms/",
        SMSView.as_view(),
        name="sms",
    ),
]
