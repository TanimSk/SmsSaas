from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from rest_framework.permissions import BasePermission
from dj_rest_auth.registration.views import RegisterView
from rest_framework import generics
from customer.serializers import (
    CustomRegistrationSerializer,
    CustomerProfileSerializer,
)


# Authenticate User Only Class
class AuthenticateOnlyCustomer(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_customer:
                return True
            else:
                return False
        return False


class ConsumerRegistrationView(RegisterView):
    serializer_class = CustomRegistrationSerializer


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [AuthenticateOnlyCustomer]

    def get_object(self):
        return self.request.user.customer

    def get_queryset(self):
        return self.request.user.customer