# webchat/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import ChatRoom, Message
from .serializers import MessageSerializer
from UserProfile.models import UserProfile

User = get_user_model()

def get_participants_data(chatroom):
    participants = []
    for participant in chatroom.participants.select_related("userprofile").all():
        user_profile = participant.userprofile
        profile_data = {
            "nickname": user_profile.nickname,
            "profilepic": {
                "id": user_profile.profilepic_id,
                "imagelink": user_profile.profilepic_id
            } if user_profile.profilepic_id else None
        }
        participants.append({"id": participant.id, "profile": profile_data})
    return participants

class ChatRoomViewSet(viewsets.ViewSet):

    @swagger_auto_schema(
        operation_description="Create a new chatroom with specified participants",
        operation_id="채팅방 생성",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user to be added as a participant'),
            },
            required=['user_id']
        ),
        responses={
            201: openapi.Response(
                description="ChatRoom created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, description='ChatRoom ID'),
                        'participants': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
                                    'profile': openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'nickname': openapi.Schema(type=openapi.TYPE_STRING, description='User nickname'),
                                            'profilepic': openapi.Schema(
                                                type=openapi.TYPE_OBJECT,
                                                properties={
                                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Profile picture ID'),
                                                    'image_url': openapi.Schema(type=openapi.TYPE_STRING, description='Profile picture URL'),
                                                }
                                            ),
                                        }
                                    )
                                }
                            )
                        ),
                        'last_message': openapi.Schema(type=openapi.TYPE_STRING, description='Last message in the chatroom'),
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid request data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
        }
    )
    #SCHEMA FOR SWAGGER. TO USE SWAGGER, RUN DJANGO DEV SERVER INSTEAD OF UVICORN
    
    def create(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Please sign in"}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = request.user
        participant_id = request.data.get('user_id')
        if not participant_id:
            return Response({"detail": "user_id is missing."}, status=status.HTTP_400_BAD_REQUEST)
        
        participant_group_ids = {user.id, participant_id}
        
        try:
            chatroom = ChatRoom.objects.annotate(
                num_participants=Count('participants'),
                num_matching=Count('participants', filter=Q(participants__id__in=participant_group_ids))
            ).get(num_participants=len(participant_group_ids), num_matching=len(participant_group_ids))
            print("Chatroom already exists")
        except ChatRoom.DoesNotExist:
            chatroom = ChatRoom.objects.create(created_at=timezone.now())
            chatroom.participants.add(user, User.objects.get(id=participant_id))
            print("Created new chatroom")

        participants = get_participants_data(chatroom)
        last_message = chatroom.message.order_by("-timestamp").first()
        response_data = {
            'id': chatroom.id,
            'participants': participants,
            'last_message': last_message.content if last_message else None
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(operation_description="Get list of all chatrooms with participants")
    def list(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Please sign in"}, status=status.HTTP_401_UNAUTHORIZED)

        user = request.user
        chatrooms = ChatRoom.objects.filter(participants=user).prefetch_related("participants__userprofile")
        
        result = []
        for chatroom in chatrooms:
            participants_info = get_participants_data(chatroom)
            last_message = chatroom.message.order_by('-timestamp').first()
            result.append({
                'id': chatroom.id,
                'participants': participants_info,
                'last_message': last_message.content if last_message else None
            })

        return Response(result)

class MessageViewSet(viewsets.ViewSet):
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('chat_room_id', openapi.IN_QUERY, description="Chat room ID", type=openapi.TYPE_STRING)
        ]
    )
    def list(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Please sign in"}, status=status.HTTP_401_UNAUTHORIZED)
        
        chat_room_id = request.query_params.get("chat_room_id")
        if not chat_room_id:
            return Response({"detail": "chat_room_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chatroom = ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            return Response({"detail": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND)
        
        messages = chatroom.message.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
