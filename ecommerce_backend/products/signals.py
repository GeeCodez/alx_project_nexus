from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product

CACHE_KEY="all_products"

@receiver(post_save,sender=Product)
def clear_products_cache_on_save(sender,instanc,**kwargs):
    cache.delete(CACHE_KEY)

@receiver(post_delete,sender=Product)
def clear_products_cache_on_delete(sender,instanc,**kwargs):
    cache.delete(CACHE_KEY)

