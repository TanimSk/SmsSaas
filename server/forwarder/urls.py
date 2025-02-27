from django.urls import path
from forwarder.views import MessageListCreateView

urlpatterns = [
    path("send/", MessageListCreateView.as_view()),
]
