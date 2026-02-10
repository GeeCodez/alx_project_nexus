from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def send_order_confirmation_email(self, user_email, order_id):
    subject = "Order Confirmation"
    message = f"Thank you for your order! Your order ID is #{order_id}."
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
    return "Email sent successfully"