from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from customer.models import Customer
from django.utils import timezone
from datetime import timedelta
import random


def generate_otp():
    return random.randint(100000, 999999)


class CustomRegistrationSerializer(RegisterSerializer):
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    name = serializers.CharField(required=True, max_length=255)
    phone_number = serializers.CharField(
        required=True,
        max_length=15,
        min_length=10,
        help_text="Enter a valid phone number."
    )

    def validate_phone_number(self, value):
        """Ensure the phone number is unique."""
        if Customer.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("User with this phone number already exists.")
        return value

    def validate_email(self, value):
        """Ensure the email is unique."""
        if Customer.objects.filter(customer__email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def get_cleaned_data(self):
        """Ensure extra fields are included in registration."""
        data = super().get_cleaned_data()
        data.update({
            "name": self.validated_data.get("name", ""),
            "phone_number": self.validated_data.get("phone_number", ""),
        })
        return data

    def save(self, request):
        """Save user and create a Customer profile."""
        user = super().save(request)
        user.is_customer = True
        user.save()

        # Create Customer instance
        customer = Customer.objects.create(
            customer=user,
            name=self.validated_data.get("name"),
            phone_number=self.validated_data.get("phone_number"),
            otp=generate_otp(),
            expired_at=timezone.localtime(timezone.now()) + timedelta(minutes=10),
        )

        return user


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        exclude = ("id", "otp", "is_verified", "expired_at")
        read_only_fields = ("customer",)
        depth = 1
