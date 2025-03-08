import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import forwarder.routing

# Ensure Django is initialized before anything else
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()  # Add this line to initialize Django properly

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(forwarder.routing.websocket_urlpatterns),
    }
)