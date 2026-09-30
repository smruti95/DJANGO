from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from app.serializers import LoginSerializer
from app.throttling import LoginRateThrottle


class LoginAPIView(APIView):
    """
    API endpoint for user login using JWT tokens.
    Authenticates via email + password.
    Method: POST
    """
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]


    @swagger_auto_schema(
        operation_id="auth_login",
        operation_summary="Login with email and password",
        operation_description=(
            "Authenticate using your registered email and password. "
            "Returns JWT access and refresh tokens."
        ),
        tags=["Authentication"],
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Login successful."),
                        "access": openapi.Schema(type=openapi.TYPE_STRING, example="eyJhbGciOiJIUzI1NiIs..."),
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING, example="eyJhbGciOiJIUzI1NiIs..."),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "email": openapi.Schema(type=openapi.TYPE_STRING, example="john@example.com"),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Login failed due to invalid credentials or validation errors.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Login failed."),
                        "errors": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate JWT tokens for the authenticated user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {
                    "message": "Login successful.",
                    "access": access_token,
                    "refresh": refresh_token,
                    "user": {
                        "email": user.email,
                    },
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "message": "Login failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
