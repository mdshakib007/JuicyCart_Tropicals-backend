from django.shortcuts import render
from rest_framework import views, viewsets
from shop.serializers import ShopSerializer
from shop.models import Shop
from users.models import Seller, Customer
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


class SpecificShop(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        shop_id = request.query_params.get('shop_id')
        if shop_id:
            queryset = Shop.objects.filter(id=shop_id)
        return queryset

class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()
    filter_backends = [SpecificShop]


class CreateShopAPIView(views.APIView):
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]


    def post(self, request):
        user = request.user

        if not hasattr(user, 'seller') or not user.seller.is_seller:
            raise PermissionDenied("You must be a verified seller to create a shop.")

        if Shop.objects.filter(owner=user.seller).exists():
            raise PermissionDenied("You already own a shop.")

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            shop = serializer.save(owner=user.seller)
            return Response({'success' : 'Your shop has been created successfully!'})
        return Response(serializer.errors)
