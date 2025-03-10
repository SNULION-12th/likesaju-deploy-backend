# webchat/serializers.py
from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField
    class Meta:
        model = Message
        fields = ["id", "chatroom", "sender", "content", "timestamp"]