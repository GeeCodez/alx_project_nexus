from rest_framework import viewsets, permissions, views
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Category, Product
from .serializers import CategorySerializer, ProductListSerializer, ProductDetailSerializer
from .pagination import StandardResultsSetPagination
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .utils import get_all_products
from rest_framework.response import Response


class PublicAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, format=None):
        return Response({
            "message": "Welcome to the public API endpoint. This endpoint is accessible without authentication.",
            "products": request.build_absolute_uri("products/"),
            "categories": request.build_absolute_uri("categories/"),
        })
    
@method_decorator(cache_page(60*15),name="list")
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category')
    permission_classes=[]
    authentication_classes=[]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    pagination_class = StandardResultsSetPagination
    # serializer_class = ProductSerializer
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name','created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def list(self,request, *args, **kwargs):
        products=get_all_products()
        products=self.filter_queryset(products)

        page=self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page,many=True)
            return self.get_paginated_response(serializer.data)

        serializer=self.get_serializer(products,many=True)
        return Response(serializer.data)