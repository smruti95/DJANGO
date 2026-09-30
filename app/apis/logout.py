from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from app.models import User


class LogoutAPIView(APIView):
    """
    API endpoint for user logout by email.
    The user provides their email address and all their active JWT refresh
    tokens are blacklisted, effectively logging them out from all sessions.
    Method: POST
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="auth_logout",
        operation_summary="Logout user by email",
        operation_description=(
    
            "All active JWT refresh tokens for that user are blacklisted, "
            
        ),
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The email address of the user to logout.",
                    example="john@example.com",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Logged out successfully.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="User john@example.com has been logged out successfully.",
                        ),
                    },
                ),
            ),
            404: openapi.Response(
                description="No user found with the provided email.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="No user found with this email address.",
                        ),
                    },
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "").strip()

        # Validate: email must be provided
        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find the user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "No user found with this email address."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get all outstanding (active) tokens for this user
        outstanding_tokens = OutstandingToken.objects.filter(user=user)

        # Blacklist each token that hasn't been blacklisted already
        blacklisted_count = 0
        for token in outstanding_tokens:
            # BlacklistedToken.objects.get_or_create avoids duplicate blacklist entries
            _, created = BlacklistedToken.objects.get_or_create(token=token)
            if created:
                blacklisted_count += 1

        return Response(
            {
                "message": f"User {email} has been logged out successfully.",
                "tokens_invalidated": blacklisted_count,
            },
            status=status.HTTP_200_OK,
        )
