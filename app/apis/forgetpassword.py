from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import PasswordResetToken
from app.serializers import ForgotPasswordSerializer
from app.tasks import send_password_reset_email_task
from app.throttling import ForgotPasswordRateThrottle


class ForgotPasswordAPIView(APIView):
    """
    API endpoint to request a password reset token sent via Celery async email task.
    Method: POST
    """
    permission_classes = [AllowAny]
    throttle_classes = [ForgotPasswordRateThrottle]


    @swagger_auto_schema(
        operation_id="auth_forgot_password",
        operation_summary="Request a password reset token via Celery email",
        operation_description=(
            "Sends a password reset token to the user's email address using Celery async task. "
            "Any previously active (unused) tokens for that user are invalidated before generating a new one."
        ),
        tags=["Authentication"],
        request_body=ForgotPasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password reset email dispatched successfully via Celery.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Password reset token generated and email task dispatched via Celery.",
                        ),
                        "token": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="a1b2c3d4e5f6...",
                            description="Reset token included in response during debug mode for convenience.",
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Unable to process password reset request.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Unable to process password reset request.",
                        ),
                        "errors": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.context['user']

            # Invalidate any previously active unused tokens for this user
            PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

            # Generate a new password reset token
            reset_token = PasswordResetToken.objects.create(user=user)

            # Trigger Celery background task to send password reset email asynchronously
            send_password_reset_email_task.delay(user.email, reset_token.token)

            response_data = {
                "message": "Password reset email task dispatched via Celery. Please check your email inbox.",
            }

            # If DEBUG is True, also include token in response for convenience in testing
            if getattr(settings, 'DEBUG', False):
                response_data["token"] = reset_token.token

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(
            {
                "message": "Unable to process password reset request.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
