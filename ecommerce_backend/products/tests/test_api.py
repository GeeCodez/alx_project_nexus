from django.urls import reverse
from rest_framework.test import APITestCase, APIClient, override_settings
from rest_framework import status
from products.models import Product, Category


class TestProducts(APITestCase):

    def setUp(self):
        self.client=APIClient()

        #Creating a mock category
        self.cat1 = Category.objects.create(name="Shoes", is_active=True)
        self.cat2 = Category.objects.create(name="Bags", is_active=True)

        #Creating a mock product
        self.prod1 = Product.objects.create(
            name="Running Shoes",
            description="Comfortable running shoes for all terrains.",
            price=79.99,
            stock=100,
            category=self.cat1,
            is_active=True
        )
        self.prod2 = Product.objects.create(
            name="Leather Bag",
            description="Stylish leather bag for everyday use.",
            price=149.99,
            stock=50,
            category=self.cat2,
            is_active=True
        )
        self.prod3 = Product.objects.create(
            name="Old Shoes",
            category=self.cat1,
            description="Inactive product",
            price=50,
            stock=0,
            is_active=False
        )

    def test_product_list_returns_active_only(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.json()['results']
        self.assertEqual(len(products), 2)  # prod3 is inactive
        product_names = [p['name'] for p in products]
        self.assertIn(self.prod1.name, product_names)
        self.assertIn(self.prod2.name, product_names)
        self.assertNotIn(self.prod3.name, product_names)

    def test_product_detail_returns_full_info(self):
        url = reverse('product-detail', args=[self.prod1.id]) # type: ignore
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['name'], self.prod1.name)
        self.assertEqual(data['description'], self.prod1.description)
        self.assertEqual(float(data['price']), self.prod1.price)
        self.assertEqual(data['stock'], self.prod1.stock)

    def test_product_list_filter_by_category(self):
        url = reverse('product-list') + f'?category={self.cat1.id}' # type: ignore
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.json()['results']
        for product in products:
            self.assertEqual(product['category_name'], self.cat1.name)

    def test_product_list_ordering(self):
        url = reverse('product-list') + '?ordering=-price'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [float(p['price']) for p in response.json()['results']]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_product_list_pagination(self):
        # creating extra products to trigger pagination
        for i in range(15):
            Product.objects.create(
                name=f"Extra{i}",
                category=self.cat1,
                description="Extra product",
                price=10 + i,
                stock=5,
                is_active=True
            )
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue('results' in data)
        self.assertEqual(len(data['results']), 10)  # comparing with default page size
        self.assertIn('next', data)
        self.assertIn('previous', data)