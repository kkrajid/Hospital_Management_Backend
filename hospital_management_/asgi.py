
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_.settings')

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter , URLRouter
from chat.routing import websocket_urlpatterns



application = ProtocolTypeRouter(
    {
        "http" : get_asgi_application() ,
        "websocket" : AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )   
        )
    }
)

