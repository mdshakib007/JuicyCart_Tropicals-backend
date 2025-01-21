from django.shortcuts import render
from listing.models import Category, Product
from listing.serializers import CategorySerializer, ProductSerializer
from rest_framework import viewsets, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from shop.models import Shop
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from users.models import Seller, Customer
from shop.models import Shop


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
        
        # Get filter parameters from the request
        product_id = self.request.query_params.get('product_id')
        category_id = self.request.query_params.get('category_id')
        name = self.request.query_params.get('name')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        # Apply filters if parameters are provided
        if product_id:
            queryset = queryset.filter(id=product_id)
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        if name:
            queryset = queryset.filter(name__icontains=name)  # Case-insensitive search
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset



class AddProductAPIView(views.APIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not hasattr(user, 'seller'):
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


class DeleteProductAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')

        if not Seller.objects.filter(user=user).exists():
            raise PermissionDenied("You must be a verified seller to delete a product.")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError("Product not found.")

        shop = Shop.objects.filter(owner=user.seller).first()
        if not shop:
            raise PermissionDenied("You do not own a shop.")

        if product.shop != shop:
            raise PermissionDenied("You can only delete products from your own shop.")

        product.delete()
        return Response({"success": "Product deleted successfully."})


class EditProductAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')

        if not Seller.objects.filter(user=user).exists():
            raise PermissionDenied("You must be a verified seller to edit a product.")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError("Product not found.")

        shop = Shop.objects.filter(owner=user.seller).first()
        if not shop:
            raise PermissionDenied("You do not own a shop.")

        if product.shop != shop:
            raise PermissionDenied("You can only edit products from your own shop.")

        # Update the product
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Product updated successfully.", "product": serializer.data})
        return Response(serializer.errors, status=400)