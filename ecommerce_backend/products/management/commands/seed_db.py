from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from products.models import Category, Product


class Command(BaseCommand):
    help = "Seed database with initial Categories and Products"

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete existing data before seeding'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding database..."))

        if options['flush']:
            self.stdout.write(self.style.WARNING("Deleting existing data..."))
            Product.objects.all().delete()
            Category.objects.all().delete()

        # Create Categories
        categories_data = [
            "Electronics",
            "Clothing",
            "Books",
            "Home & Kitchen",
        ]

        categories = {}
        for name in categories_data:
            category, created = Category.objects.get_or_create(name=name)
            categories[name] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {name}"))

        # Create Products
        products_data = [
            {
                "name": "Laptop",
                "category": "Electronics",
                "description": "High performance laptop",
                "price": Decimal("1200.00"),
                "stock": 10,
            },
            {
                "name": "T-Shirt",
                "category": "Clothing",
                "description": "100% cotton t-shirt",
                "price": Decimal("25.00"),
                "stock": 50,
            },
            {
                "name": "Django for Beginners",
                "category": "Books",
                "description": "Learn Django step by step",
                "price": Decimal("40.00"),
                "stock": 30,
            },
        ]

        for item in products_data:
            product, created = Product.objects.get_or_create(
                name=item["name"],
                defaults={
                    "category": categories[item["category"]],
                    "description": item["description"],
                    "price": item["price"],
                    "stock": item["stock"],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created product: {item['name']}"))

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
