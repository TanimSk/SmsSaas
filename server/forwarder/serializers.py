from rest_framework import serializers
from forwarder.models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class BulkMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=200)
    recipients = serializers.ListField(child=serializers.CharField(max_length=15))

    def create(self, validated_data):
        # loop through phone_numbers and create a message for each
        messages = []
        for recipient in validated_data["recipients"]:
            message = Message.objects.create(
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

