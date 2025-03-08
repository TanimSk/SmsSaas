from django.shortcuts import render
from dj_rest_auth.registration.views import LoginView
from django.contrib.auth import login as django_login
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission, IsAuthenticated
from dj_rest_auth.views import PasswordChangeView
from .serializers import CustomPasswordChangeSerializer
from rest_framework import status
from django.utils import timezone
from customer.serializers import generate_otp

# models
from forwarder.models import Message

# authentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class LoginWthPermission(APIView):
    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        self.login()

        return self.get_response()

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response(
                {
                    "success": False,
                    "message": "Invalid credentials",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.is_customer and not user.customer.is_verified:
            return Response(
                {
                    "success": False,
                    "message": "Please verify your phone number with OTP.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Construct the response
        response_data = {
            "success": True,
            "access": access_token,
            "refresh": str(refresh),
            "user": {
                "pk": user.pk,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "role": "CUSTOMER" if user.is_customer else "ADMIN",
        }

        # Set access and refresh token to the cookie
        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=60 * 60 * 24 * 7,  # 1 week
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="None",
            max_age=60 * 60 * 24 * 30,  # 1-month expiration
        )
        return response


class CustomLogout(APIView):
    def post(self, request):
        # Delete JWT token from the cookie
        response = Response(
            {"success": True, "message": "Logged out successfully"},
            status=status.HTTP_200_OK,
        )

        # Set cookies to expire immediately
        response.set_cookie(
            "access_token",
            "",
            expires=0,
            path="/",
            httponly=True,
            secure=True,
            samesite="None",
        )
        response.set_cookie(
            "refresh_token",
            "",
            expires=0,
            path="/",
            httponly=True,
            secure=True,
            samesite="None",
        )

        # Ensure they are deleted
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

        return response


# change password
class CustomPasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomPasswordChangeSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            # Check if old password is correct
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"success": False, "message": "Old password is incorrect."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Set the new password
            user.set_password(serializer.validated_data["new_password1"])
            user.save()

            return Response(
                {"success": True, "message": "Password has been changed successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTP(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        otp = request.data.get("otp")
        user = request.user

        if user.is_customer and user.customer.otp == otp:
            if user.customer.expired_at > timezone.now():
                user.customer.is_verified = True
                user.customer.save()

                return Response(
                    {"success": True, "message": "Phone number has been verified."},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"success": False, "message": "OTP has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"success": False, "message": "Invalid OTP"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResendOTP(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        if user.is_customer:
            if user.customer.is_verified:
                return Response(
                    {"success": False, "message": "Phone number is already verified."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if user.customer.expired_at > timezone.now():
                return Response(
                    {
                        "success": False,
                        "message": "Cannot resend OTP before it expires.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            otp = generate_otp()
            user.customer.otp = otp
            user.customer.expired_at = timezone.now() + timezone.timedelta(minutes=10)
            user.customer.save()

            # send otp to user
            Message.objects.create(
                status="QUEUED",
                recipient=user.customer.phone_number,
                message=f"Your OTP for CloudSMS BD is {otp}",
            )

            return Response(
                {"success": True, "message": "OTP has been sent successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": False, "message": "Invalid Request"},
            status=status.HTTP_400_BAD_REQUEST,
        )
