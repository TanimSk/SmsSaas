from forwarder.serializers import MessageSerializer, BulkMessageSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from forwarder.sms_validator import valid_sms
from administrator.models import AdminInfo
from customer.models import Customer


class MessageListCreateView(APIView):
    def post(self, request):

        if request.GET.get("type") == "bulk":
            serializer = BulkMessageSerializer(data=request.data)
        else:
            serializer = MessageSerializer(data=request.data)

        if not (
            request.GET.get("key") or (request.user and request.user.is_authenticated)
        ):
            return Response(
                {"success": False, "message": "API key is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if serializer.is_valid(raise_exception=True):
            try:
                if request.user and request.user.is_authenticated:
                    user = Customer.objects.get(customer=request.user)
                else:
                    user = Customer.objects.get(api_key=request.GET.get("key"))

            except Customer.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "message": "Invalid API key",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            admin_info = AdminInfo.objects.first()

            if valid_sms(serializer.validated_data["message"]):
                # --- Check if user has enough quota ---
                if user.sms_quota == 0:
                    return Response(
                        {
                            "success": False,
                            "message": "SMS quota exceeded, please buy more credits",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # --- Check if admin has enough quota ---
                if admin_info.total_sms_quota == 0:
                    return Response(
                        {
                            "success": False,
                            "message": "Please contact the administrator to buy more credits, admin quota exceeded",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # reduce user quota
                user.sms_quota -= 1
                user.save()

                # reduce overall quota
                admin_info.total_sms_quota -= 1
                admin_info.save()
                
                # add message to queue
                serializer.validated_data["status"] = "QUEUED"
                serializer.validated_data["customer"] = user
                serializer.save()

                return Response(
                    {"success": True, **serializer.data}, status=status.HTTP_201_CREATED
                )
            else:
                serializer.validated_data["status"] = "REJECTED"
                serializer.validated_data["customer"] = user
                serializer.save()
                return Response(
                    {
                        "success": False,
                        "message": "Inappropriate content is not allowed",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )        
