from django.urls import path
from app.apis import (
    RegisterAPIView,
    LoginAPIView,
    ForgotPasswordAPIView,
    ResetPasswordAPIView,
    LogoutAPIView,
    UserProfileAPIView,
)



app_name = 'api'

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('forget-password/', ForgotPasswordAPIView.as_view(), name='forget-password'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('profile/', UserProfileAPIView.as_view(), name='profile'),
]

