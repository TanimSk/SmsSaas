from django.db import models

class Message(models.Model):
    STATUS_CHOICES = [
        ("QUEUED", "Queued"),
        ("SENT", "Sent"),
        ("RECEIVED", "Received"),
        ("FAILED", "Failed"),
    ]    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="QUEUED")
    recipient = models.CharField(max_length=15)
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
