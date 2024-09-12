from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import UserProfile

from .serializers import UserSerializer, UserProfileSerializer
from .request_serializers import SignUpRequestSerializer, SignInRequestSerializer, TokenRefreshRequestSerializer, UserProfileUpdateRequestSerializer, SignOutRequestSerializer

def set_token_on_response_cookie(user, status_code) -> Response:
    token = RefreshToken.for_user(user)
    user_profile = UserProfile.objects.get(user=user)
    serialized_data = UserProfileSerializer(user_profile).data
    res = Response(serialized_data, status=status_code)
    res.set_cookie("refresh_token", value=str(token))
    res.set_cookie("access_token", value=str(token.access_token))
    return res

class SignUpView(APIView):
    @swagger_auto_schema(
        operation_id="회원가입",
        operation_description="회원가입을 진행합니다.",
        request_body=SignUpRequestSerializer,
        responses={201: UserProfileSerializer, 400: "Bad Request"},
    )
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user_serializer.validated_data["password"] = make_password(
                user_serializer.validated_data["password"]
            )
            user = user_serializer.save()
            user.save()

        UserProfile.objects.create(
            user=user
        )

        return set_token_on_response_cookie(user, status_code=status.HTTP_201_CREATED)

class SignInView(APIView):
    @swagger_auto_schema(
        operation_id="로그인",
        operation_description="로그인을 진행합니다.",
        request_body=SignInRequestSerializer,
        responses={200: UserProfileSerializer, 404: "Not Found", 400: "Bad Request"},
    )
    def post(self, request):
        user = User.objects.filter(username=request.data["username"]).first()
        if user is None:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(request.data["password"]):
            return Response({"message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)

        return set_token_on_response_cookie(user, status_code=status.HTTP_200_OK)
    
class TokenRefreshView(APIView):
    @swagger_auto_schema(
        operation_id="토큰 재발급",
        operation_description="access 토큰을 재발급 받습니다.",
        request_body=TokenRefreshRequestSerializer,
        responses={200: UserSerializer, 400: "Bad Request", 401: "Unauthorized"},
        manual_parameters=[openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)]
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "no refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            RefreshToken(refresh_token).verify()
        except:
            return Response(
                {"detail": "please signin again."}, status=status.HTTP_401_UNAUTHORIZED
            )
        new_access_token = str(RefreshToken(refresh_token).access_token)
        response = Response({"detail": "token refreshed"}, status=status.HTTP_200_OK)
        response.set_cookie("access_token", value=str(new_access_token), httponly=True)
        return response


class SignOutView(APIView):
    @swagger_auto_schema(
        operation_id="로그아웃",
        operation_description="로그아웃을 진행합니다.",
        request_body=SignOutRequestSerializer,
        responses={204: "No Content", 400: "Bad Request", 401: "Unauthorized"},
        manual_parameters=[openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)]
    )
    def post(self, request):

        if not request.user.is_authenticated:
            return Response(
                {"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED
            )

        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "no refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )
        RefreshToken(refresh_token).blacklist()

        return Response(status=status.HTTP_204_NO_CONTENT)

class UserProfileListView(APIView):
    @swagger_auto_schema(
        operation_id="유저 정보 확인",
        operation_description="등록된 모든 유저 정보를 가져옵니다",
        request_body=None,
        responses={200: UserProfileSerializer(many=True), 401: "please signin"},
        manual_parameters=[openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)]
    )
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED)
        user_profile = UserProfile.objects.all()
        serializer = UserProfileSerializer(user_profile, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserProfileDetailView(APIView):
    @swagger_auto_schema(
        operation_id="유저 정보 확인",
        operation_description="토큰을 기반으로, 유저 세부 정보를 가져옵니다.",
        request_body=None,
        responses={200: UserProfileSerializer, 404: "UserProfile Not found.", 401: "please signin"},
        manual_parameters=[openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)]
    )
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_profile = UserProfile.objects.get(user=user)
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"detail": "UserProfile Not found."}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_id="유저 정보 수정",
        operation_description="유저 개인 프로필 정보(닉네임, 프로필 사진)를 수정합니다.",
        request_body=UserProfileUpdateRequestSerializer,
        responses={200: UserProfileSerializer, 400: "[profilepic_id, nickname] fields missing.", 401: "please signin", 404: "UserProfile Not found."},
        manual_parameters=[openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)]
    )
    def put(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_profile = UserProfile.objects.get(user=user)
            profilepic_id = request.data.get("profilepic_id")
            nickname = request.data.get("nickname")
            if not profilepic_id or not nickname:
                return Response({"detail": "[profilepic_id, nickname] fields missing."}, status=status.HTTP_400_BAD_REQUEST)
            user_profile.profilepic_id=profilepic_id
            user_profile.nickname = nickname
            user_profile.save()
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"detail": "UserProfile Not found."}, status=status.HTTP_404_NOT_FOUND)
        
class CheckUsernameView(APIView):
    @swagger_auto_schema(
        operation_id="유저명 중복 확인",
        operation_description="유저명이 이미 존재하는지 확인합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="중복을 확인할 유저명",
                )
            },
        ),
        responses={200: "Username is available", 400: "Username already exists"},
    )
    def post(self, request):
        username = request.data.get("username")
        if User.objects.filter(username=username).exists():
            return Response({"message": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Username is available"}, status=status.HTTP_200_OK)