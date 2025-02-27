from forwarder.serializers import MessageSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer


# def send_message(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         message = data.get("messageBody", "")
#         Message.objects.create()

#         # channel_layer = get_channel_layer()
#         # async_to_sync(channel_layer.group_send)(
#         #     "chat_group",
#         #     {"type": "chat.message", "message": message},
#         # )

#         return JsonResponse({"status": "Message sent via WebSocket"})
#     return JsonResponse({"error": "Invalid request"}, status=400)


class MessageListCreateView(APIView):
    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
