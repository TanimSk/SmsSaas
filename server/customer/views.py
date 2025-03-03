from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from rest_framework.permissions import BasePermission
from dj_rest_auth.registration.views import RegisterView
from rest_framework import generics
from customer.serializers import (
    CustomRegistrationSerializer,
    CustomerProfileSerializer,
)
from forwarder.serializers import MessageSerializer
from forwarder.models import Message

from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
import uuid


# Authenticate User Only Class
class AuthenticateOnlyCustomer(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_customer:
                return True
            else:
                return False
        return False


# Pagination Config
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 500
    page_query_param = "p"


class ConsumerRegistrationView(RegisterView):
    serializer_class = CustomRegistrationSerializer


class CustomerProfileView(APIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [AuthenticateOnlyCustomer]

    def get(self, request):
        customer = request.user.customer
        serializer = self.serializer_class(customer)
        return JsonResponse(serializer.data)

    def put(self, request):
        customer = request.user.customer
        serializer = self.serializer_class(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {
                    "success": True,
                    "message": "Profile updated successfully.",
                }
            )
        return JsonResponse(
            {
                "success": False,
                "message": serializer.errors,
            }
        )


class APIKeyView(APIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [AuthenticateOnlyCustomer]

    def get(self, request, *args, **kwargs):
        customer = request.user.customer
        return JsonResponse({"api_key": customer.api_key})

    def post(self, request, *args, **kwargs):
        customer = request.user.customer
        customer.api_key = "ssb_" + str(uuid.uuid4())
        customer.save()
        return JsonResponse({"api_key": customer.api_key})

    def delete(self, request, *args, **kwargs):
        customer = request.user.customer
        customer.api_key = None
        customer.save()
        return JsonResponse({"message": "API key deleted successfully."})


class SMSView(APIView):
    permission_classes = [AuthenticateOnlyCustomer]

    def get(self, request, *args, **kwargs):
        messages = Message.objects.filter(customer=request.user.customer)
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(messages, request)
        serializer = MessageSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)