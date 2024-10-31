import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'likesaju.settings')

django_application = get_asgi_application() # init django application

from  . import urls 
from channels.routing import ProtocolTypeRouter, URLRouter
from webchat.middleware import JWTAuthMiddleWare

application = ProtocolTypeRouter(
    {
        # FILL HERE AT WEBSOCKET SEMINAR
    }
)
