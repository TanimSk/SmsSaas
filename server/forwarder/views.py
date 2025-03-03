from forwarder.serializers import MessageSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from forwarder.sms_validator import valid_sms
from administrator.models import AdminInfo
from customer.models import Customer


class MessageListCreateView(APIView):
    def post(self, request):
        serializer = MessageSerializer(data=request.data)

        if not request.GET.get("key"):
            return Response(
                {"success": False, "message": "API key is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if serializer.is_valid():
            if valid_sms(serializer.validated_data["message"]):
                # reduce user quota
                try:
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

                user.sms_quota -= 1
                user.save()

                # reduce overall quota
                admin_info.total_sms_quota -= 1
                admin_info.save()

                serializer.validated_data["customer"] = user
                serializer.save()
                serializer.data.pop("inappropiate_content")
                return Response(
                    {"success": True, **serializer.data}, status=status.HTTP_201_CREATED
                )
            else:
                serializer.validated_data["inappropiate_content"] = True
                serializer.save()
                return Response(
                    {
                        "success": False,
                        "message": "Inappropriate content is not allowed",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
