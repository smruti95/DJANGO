from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.serializers import ResetPasswordSerializer
from app.throttling import ResetPasswordRateThrottle


class ResetPasswordAPIView(APIView):
    """
    API endpoint to reset password using a valid reset token.
    Method: POST
    """
    permission_classes = [AllowAny]
    throttle_classes = [ResetPasswordRateThrottle]


    @swagger_auto_schema(
        operation_id="auth_reset_password",
        operation_summary="Reset password using a reset token",
        operation_description=(
            "Resets the user's password using a valid one-time reset token obtained from the "
            "**Forgot Password** endpoint. The token is invalidated after use to prevent replay attacks."
        ),
        tags=["Authentication"],
        request_body=ResetPasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password has been successfully reset.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Password has been successfully reset. You can now login with your new password.",
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Password reset failed due to an invalid or expired token or validation error.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Password reset failed."),
                        "errors": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            reset_token = serializer.validated_data['reset_token']
            new_password = serializer.validated_data['new_password']
            user = reset_token.user

            # Update password securely
            user.set_password(new_password)
            user.save()

            # Mark token as used to prevent replay attacks
            reset_token.is_used = True
            reset_token.save()

            return Response(
                {
                    "message": "Password has been successfully reset",
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "message": "Password reset failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
