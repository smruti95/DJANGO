import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email_task(self, email: str, token: str):
    """
    Celery task to send password reset token/link asynchronously to the user's email address.
    """
    subject = "Password Reset Request"
    message = (

        f"Your reset token is:\n\n{token}\n\n"
        f"This token is valid for 15 minutes.\n"
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@authsession.com')

    try:
        logger.info(f"Sending password reset email to {email}")
        sent_count = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"Successfully dispatched password reset email to {email}.")
        return {"status": "success", "recipient": email, "sent_count": sent_count}
    except Exception as exc:
        logger.error(f"Failed to send password reset email to {email}: {exc}")
        raise self.retry(exc=exc)
