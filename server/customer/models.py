from django.db import models


class Customer(models.Model):
    customer = models.OneToOneField(
        "administrator.User",
        on_delete=models.CASCADE,
        related_name="customer",
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    api_key = models.CharField(null=True, blank=True, max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    # sms, 5 sms is free for each customer
    sms_quota = models.IntegerField(default=10)

    # validation
    otp = models.CharField(null=True, blank=True, max_length=6)
    expired_at = models.DateTimeField(null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name
