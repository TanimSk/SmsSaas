import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import forwarder.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(forwarder.routing.websocket_urlpatterns),
    }
)