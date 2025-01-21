from django.shortcuts import render
from listing.models import Category, Product
from listing.serializers import CategorySerializer, ProductSerializer
from rest_framework import viewsets, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from shop.models import Shop
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(id = category_id)
        return queryset


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(id=product_id)
        return queryset


class AddProductAPIView(views.APIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not hasattr(user, 'seller') or not user.seller.is_seller:
            raise PermissionDenied("You must be a verified seller to list a product.")
        
        try:
            shop = Shop.objects.get(owner=user.seller)
        except Shop.DoesNotExist:
            raise PermissionDenied("You do not own a shop.")
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            product = serializer.save(shop=shop)
            return Response({'success': 'Product added successfully!'})
        return Response(serializer.errors)