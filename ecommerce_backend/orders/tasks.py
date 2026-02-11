from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Order
from products.models import Product

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def send_order_confirmation_email(self, user_email, order_id):
    subject = "Order Confirmation"
    message = f"Thank you for your order! Your order ID is #{order_id} has been paid for.\
    It is currently being processed."
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
    return "Email sent successfully"

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def send_shipping_email(order: Order):
    send_mail(
        subject=f"Your Order #{order.id} Has Been Shipped",
        message="Your order has been shipped and is on the way.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        fail_silently=False,
    )


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def send_delivery_email(order: Order):
    send_mail(
        subject=f"Your Order #{order.id} Has Been Delivered",
        message="Your order has been delivered. Thank you for shopping with us!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        fail_silently=False,
    )
