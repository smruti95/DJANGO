from django.core.cache import cache
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.serializers import UserProfileSerializer
from app.throttling import UserProfileRateThrottle


class UserProfileAPIView(APIView):
    """
    API Endpoint for User Profile management.
    Demonstrates Caching (cache.get / cache.set / cache.delete) and Rate Limiting.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserProfileRateThrottle]

    def get_cache_key(self, user_id):
        return f"user_profile_{user_id}"

    @swagger_auto_schema(
        operation_id="user_profile_get",
        operation_summary="Get user profile (Cached)",
        operation_description=(
            "Retrieves profile details for the authenticated user. "
            "Uses Redis/Django Cache (15-minute TTL). Returns 'X-Cache' header (HIT or MISS)."
        ),
        tags=["User Profile"],
        responses={
            200: openapi.Response(
                description="Profile details retrieved.",
                schema=UserProfileSerializer,
            ),
            401: "Unauthorized - Token missing or invalid.",
        },
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        cache_key = self.get_cache_key(user.id)

        # 1. Try to retrieve cached data
        cached_profile = cache.get(cache_key)
        if cached_profile:
            response = Response(
                {
                    "message": "User profile retrieved successfully (from Cache).",
                    "cached": True,
                    "profile": cached_profile,
                },
                status=status.HTTP_200_OK,
            )
            response["X-Cache"] = "HIT"
            return response

        # 2. Cache Miss: Fetch from database
        serializer = UserProfileSerializer(user)
        profile_data = serializer.data

        # 3. Store in cache for 15 minutes (900 seconds)
        cache.set(cache_key, profile_data, timeout=900)

        response = Response(
            {
                "message": "User profile retrieved successfully (from Database).",
                "cached": False,
                "profile": profile_data,
            },
            status=status.HTTP_200_OK,
        )
        response["X-Cache"] = "MISS"
        return response

    @swagger_auto_schema(
        operation_id="user_profile_update",
        operation_summary="Update user profile (Invalidates Cache)",
        operation_description=(
            "Updates profile details (e.g. first_name, last_name) for authenticated user. "
            "Automatically invalidates the cached profile in Redis/Django cache."
        ),
        tags=["User Profile"],
        request_body=UserProfileSerializer,
        responses={
            200: openapi.Response(
                description="Profile updated successfully.",
                schema=UserProfileSerializer,
            ),
            400: "Invalid profile data.",
            401: "Unauthorized - Token missing or invalid.",
        },
    )
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Invalidate cached profile entry to force fresh data on next GET
            cache_key = self.get_cache_key(user.id)
            cache.delete(cache_key)

            return Response(
                {
                    "message": "User profile updated successfully. Cache invalidated.",
                    "profile": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "Failed to update profile.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
