from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Product
from orders.models import Order, OrderItem

User = get_user_model()


class OrdersAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="password123")
        self.client.force_authenticate(user=self.user)

        self.other_user = User.objects.create_user(email="other@example.com", password="password123")

        self.p1 = Product.objects.create(name="Product 1", price=50, stock=10, is_active=True)
        self.p2 = Product.objects.create(name="Product 2", price=100, stock=5, is_active=True)

    def test_create_order_success(self):
        payload = {
            "items": [
                {"product_id": self.p1.id, "quantity": 2},
                {"product_id": self.p2.id, "quantity": 1},
            ]
        }
        response = self.client.post("/api/orders/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data
        self.assertEqual(data["total_amount"], "200.00")
        self.assertEqual(len(data["order_items"]), 2)

        order = Order.objects.get(id=data["id"])
        self.assertEqual(order.total_amount, Decimal("200.00"))

    def test_create_order_insufficient_stock(self):
        payload = {"items": [{"product_id": self.p1.id, "quantity": 20}]}
        response = self.client.post("/api/orders/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            "Insufficient stock" in str(response.data)
        )


    def test_order_ownership(self):
        # Create an order for another user
        order = Order.objects.create(user=self.other_user, total_amount=50, currency="GHS")
        response = self.client.get(f"/api/orders/{order.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    
    def test_cancel_order(self):
        payload = {"items": [{"product_id": self.p1.id, "quantity": 1}]}
        create_resp = self.client.post("/api/orders/", payload, format="json")
        order_id = create_resp.data["id"]

        cancel_resp = self.client.post(f"/api/orders/{order_id}/cancel/")
        self.assertEqual(cancel_resp.status_code, status.HTTP_200_OK)

        order = Order.objects.get(id=order_id)
        self.assertEqual(order.status, "cancelled")

    
    def test_cannot_cancel_shipped_or_delivered_order(self):
        shipped_order = Order.objects.create(user=self.user, total_amount=50, status="shipped", currency="GHS")
        delivered_order = Order.objects.create(user=self.user, total_amount=50, status="delivered", currency="GHS")

        # Shipped
        resp_shipped = self.client.post(f"/api/orders/{shipped_order.id}/cancel/")
        self.assertEqual(resp_shipped.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot cancel", resp_shipped.data["detail"])

        # Delivered
        resp_delivered = self.client.post(f"/api/orders/{delivered_order.id}/cancel/")
        self.assertEqual(resp_delivered.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot cancel", resp_delivered.data["detail"])

    
    def test_order_list_queries_sanity(self):
        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        # create multiple orders
        for i in range(5):
            order = Order.objects.create(user=self.user, total_amount=100, currency="GHS")
            for p in [self.p1, self.p2]:
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    product_name=p.name,
                    quantity=1,
                    unit_price=p.price,
                    total_price=p.price
                )

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get("/api/orders/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertLessEqual(len(ctx), 10)