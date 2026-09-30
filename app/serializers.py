from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from app.models import PasswordResetToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Accepts email, first_name, last_name, password, confirm_password.
    Auto-generates username from email prefix.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'password',
            'confirm_password',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def _generate_unique_username(self, email):
        """Generate a unique username from the email prefix."""
        base_username = email.split('@')[0][:30]  # max 30 chars
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        return username

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        email = validated_data['email']
        username = self._generate_unique_username(email)
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password'],
        )
        return user




class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Supports login using email + password.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Registered email address"
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"}
    )

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        # Look up user by email
        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        # Authenticate via username (Django's backend needs username)
        request = self.context.get("request")
        user = authenticate(
            request=request,
            username=user_obj.username,
            password=password
        )

        # Invalid credentials
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        # Inactive user
        if not user.is_active:
            raise serializers.ValidationError("This user account is inactive.")

        # Add authenticated user to validated data
        attrs["user"] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for requesting password reset token."""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No active user found with this email address.")

        if not user.is_active:
            raise serializers.ValidationError("This user account is inactive.")

        self.context['user'] = user
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for resetting password using the generated token."""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    confirm_new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    def validate(self, attrs):
        token_str = attrs.get('token')
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')

        if new_password != confirm_new_password:
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match."})

        try:
            reset_token = PasswordResetToken.objects.select_related('user').get(token=token_str)
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid or unknown reset token."})

        if not reset_token.is_valid():
            raise serializers.ValidationError({"token": "This reset token is expired or has already been used."})

        attrs['reset_token'] = reset_token
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing and updating user profile details.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'email', 'username', 'is_active', 'date_joined']

