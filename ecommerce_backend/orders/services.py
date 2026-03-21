from django.db import transaction
from django.conf import settings
from .models import Order
from django.db import transaction
from .tasks import send_shipping_email, send_delivery_email


@transaction.atomic
def update_order_status(order, new_status):
    old_status = order.status

    order.status = new_status
    order.save()

    transaction.on_commit(lambda: trigger_celery_tasks(order, old_status, new_status))


def trigger_celery_tasks(order, old_status, new_status):

    if new_status == Order.Status.SHIPPED:
        send_shipping_email.delay(order.id) #type: ignore

    if new_status == Order.Status.DELIVERED:
        send_delivery_email.delay(order.id) #type: ignore
