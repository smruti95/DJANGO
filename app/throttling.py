from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """
    Rate throttle for user login endpoint.
    Limits login attempts per IP address to prevent brute-force attacks.
    """
    scope = 'login'

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class RegisterRateThrottle(SimpleRateThrottle):
    """
    Rate throttle for user registration endpoint.
    Limits registration attempts per IP address to prevent spam bot accounts.
    """
    scope = 'register'

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class ForgotPasswordRateThrottle(SimpleRateThrottle):
    """
    Rate throttle for forgot password request endpoint.
    Limits reset email dispatch attempts per IP address.
    """
    scope = 'forgot_password'

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class ResetPasswordRateThrottle(SimpleRateThrottle):
    """
    Rate throttle for reset password endpoint.
    Limits password reset submissions per IP address.
    """
    scope = 'reset_password'

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class UserProfileRateThrottle(SimpleRateThrottle):
    """
    Rate throttle for User Profile endpoint.
    Limits authenticated user profile requests to prevent resource abuse.
    """
    scope = 'user_profile'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            return f"throttle_user_{request.user.pk}"
        return self.get_ident(request)
