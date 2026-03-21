import uuid
import requests
from django.conf import settings
from .models import Payment
from django.db import transaction
import hmac
import hashlib
from orders.tasks import send_order_confirmation_email


def generate_payment_reference():
    return f"pay_{uuid.uuid4().hex}"


def initialize_paystack_payment(order, user, email):
    reference = generate_payment_reference()
    payment = Payment.objects.create(
        order=order,
        user=user,
        amount=order.total_amount,
        reference=reference,
        status=Payment.Status.INITIALIZED,
        provider=Payment.Provider.PAYSTACK,
    )

    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "amount": int(payment.amount * 100),
        "reference": payment.reference,
        "currency": payment.currency,
        "channels": ["mobile_money"],
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    data = response.json()

    if not data.get("status"):
        payment.status = Payment.Status.FAILED
        payment.provider_response = data
        payment.save(update_fields=["provider_response", "status"])
        raise ValueError(f"Paystack error: {data.get('message')}")

    payment.provider_response = data
    payment.status = Payment.Status.PENDING
    payment.save(update_fields=["provider_response", "status"])

    return payment, data["data"]["authorization_url"]


def verify_paystack_payment(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    response = requests.get(url, headers=headers, timeout=30)
    return response.json()


def process_paystack_webhook(event_data):
    reference=event_data["data"]["reference"]

    try:
        with transaction.atomic():
            payment=Payment.objects.select_for_update().get(reference=reference)
            if payment.status==Payment.Status.SUCCESS:
                return

            verification=verify_paystack_payment(reference)

            if verification["data"]["status"]=="success":
                payment.status=Payment.Status.SUCCESS
                payment.provider_response=verification
                payment.save(update_fields=["status","provider_response"])

                order=payment.order
                order.status="paid"
                order.payment_reference=reference
                order.save(update_fields=["status","payment_reference"])

                email=order.user.email  # type: ignore

                if email:
                    transaction.on_commit(lambda: send_order_confirmation_email.delay(user_email=email,order_id=order.id))  # type: ignore

            else:
                payment.status=Payment.Status.FAILED
                payment.provider_response=verification
                payment.save(update_fields=["status","provider_response"])

    except Payment.DoesNotExist:
        return


def verify_paystack_signature(request_body, signature):
    computed = hmac.new(
        settings.PAYSTACK_WEBHOOK_SECRET.encode(),
        msg=request_body,
        digestmod=hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed, signature)