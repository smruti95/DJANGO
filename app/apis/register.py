from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.serializers import UserSerializer
from app.throttling import RegisterRateThrottle


class RegisterAPIView(APIView):
    """
    for user registration.
    """
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]


    @swagger_auto_schema(
        operation_id="auth_register",
        operation_summary="Register a new user",
        operation_description=(
            "Creates a new user account. "
        ),
        tags=["Authentication"],
        request_body=UserSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="User registered successfully."
                        ),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "email": openapi.Schema(type=openapi.TYPE_STRING, example="john@example.com"),
                                "first_name": openapi.Schema(type=openapi.TYPE_STRING, example="John"),
                                "last_name": openapi.Schema(type=openapi.TYPE_STRING, example="Doe"),
                                "username": openapi.Schema(type=openapi.TYPE_STRING, example="john"),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Registration failed due to validation errors.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Registration failed."),
                        "errors": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "message": "Registration failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
