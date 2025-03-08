from rest_framework import serializers
from forwarder.models import Message
from customer.models import Customer


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message        
        exclude = ("customer",)


class BulkMessageSerializer(serializers.Serializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=False)
    message = serializers.CharField(max_length=200)
    recipients = serializers.ListField(child=serializers.CharField(max_length=15))

    def create(self, validated_data):
        # loop through phone_numbers and create a message for each
        messages = []
        for recipient in validated_data["recipients"]:
            message = Message.objects.create(
                customer=validated_data["customer"],
                message=validated_data["message"],
                recipient=recipient,
                status="QUEUED",
            )
            messages.append(message)
        return {
            "message": validated_data["message"],
            "recipients": validated_data["recipients"],
            "status": "QUEUED",
            "created_at": messages[0].created_at,
            "sent_at": None,            
        }
    
    def to_representation(self, instance):
        return {
            "message": instance["message"],
            "recipients": instance["recipients"],
            "status": instance["status"],
            "created_at": instance["created_at"],
            "sent_at": instance["sent_at"],
        }

