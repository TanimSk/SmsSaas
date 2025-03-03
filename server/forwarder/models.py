from django.db import models
from uuid import uuid4


class Message(models.Model):
    customer = models.ForeignKey(
        "customer.Customer",
        on_delete=models.CASCADE,
        related_name="messages",
        blank=True,
        null=True,
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    STATUS_CHOICES = [
        ("QUEUED", "Queued"),
        ("SENT", "Sent"),
        ("RECEIVED", "Received"),
        ("FAILED", "Failed"),
        ("REJECTED", "Rejected"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="QUEUED")
    recipient = models.CharField(max_length=15)
    message = models.CharField(max_length=160)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
