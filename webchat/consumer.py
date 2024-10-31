from asgiref.sync import async_to_sync
from rest_framework import status
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from django.db.models import Count, Q
from django.utils import timezone

User = get_user_model()
user_channel_name_dict = {}

class WebChatConsumer(JsonWebsocketConsumer):
    groups = ["broadcast"]

    def __init__(self, *args, **kwargs):
        # FILL HERE AT WEBSOCKET SEMINAR
        pass

    def connect(self):
        # FILL HERE AT WEBSOCKET SEMINAR
        pass

    def receive_json(self, content):
        # FILL HERE AT WEBSOCKET SEMINAR
        pass

    def chat_message(self, event):
        # FILL HERE AT WEBSOCKET SEMINAR
        pass

    def disconnect(self, close_code):
        # FILL HERE AT WEBSOCKET SEMINAR
        pass