import jwt
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def get_user(scope):
    # FILL HERE AT WEBSOCKET SEMINAR
    pass

class JWTAuthMiddleWare:
    def __init__(self, app):
        self.app = app
        # FILL HERE AT WEBSOCKET SEMINAR

    async def __call__(self, scope, receive, send):
        # FILL HERE AT WEBSOCKET SEMINAR
        pass
