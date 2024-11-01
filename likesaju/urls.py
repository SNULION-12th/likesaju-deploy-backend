from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from webchat.views import MessageViewSet, ChatRoomViewSet
from webchat.consumer import WebChatConsumer
from rest_framework import permissions

# Swagger Schema 설정
schema_view = get_schema_view(
    openapi.Info(
        title="LIKESAJU API",
        default_version='v1',
        description="멋쟁이 사주처럼 api 테스트 페이지",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Router 설정
router = DefaultRouter()
router.register("api/messages", MessageViewSet, basename="message")
router.register("api/chatrooms", ChatRoomViewSet, basename="chatroom")

# URL 패턴 설정
urlpatterns = [
    path("admin/", admin.site.urls),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/user/", include("UserProfile.urls")),
    path("api/point/", include("Point.urls")),
    path("api/payment/", include("Payment.urls")),
] + router.urls

# 웹소켓 URL 패턴 설정
websocket_urlpatterns = [
    # FILL HERE AT WEBSOCKET SEMINAR
    path("ws/chat/", WebChatConsumer.as_asgi()),
]