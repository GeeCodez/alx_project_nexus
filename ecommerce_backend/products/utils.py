from django.core.cache import cache
from .models import Product


def get_all_products():
    products = cache.get("all_products")

    if not products:
        products =Product.objects.filter(is_active=True).select_related('category')
        cache.set("all_products", products, timeout=60 * 60)

    return products