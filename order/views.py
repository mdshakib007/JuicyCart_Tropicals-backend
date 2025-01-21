from django.shortcuts import render
from rest_framework import views, viewsets
from order.models import Order
from order.serializers import OrderSerializer
from rest_framework.filters import BaseFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from listing.models import Product
from django.db import transaction
from users.models import Customer, Seller


class SpecificOrder(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        order_id = request.query_params.get('order_id')
        if order_id:
            queryset = Order.objects.filter(id=order_id)
        return queryset

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    filter_backends = [SpecificOrder]


class PlaceOrderAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not Customer.objects.filter(user=user).exists():
            raise PermissionDenied("You do not have access to buy any product.")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError({"error": "Invalid product ID."})

        if product.available < int(quantity):
            raise ValidationError({"error": "Not enough stock available."})

        with transaction.atomic(): 
            product.available -= int(quantity)
            product.sold += int(quantity)
            product.save()

            order = Order.objects.create(
                product=product,
                customer=user.customer,
                quantity=quantity,
                total_price=product.price * int(quantity),
            )
        serializer = OrderSerializer(order)

        return Response(serializer.data)



class CancelOrderAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        order_id = int(request.data.get('order_id'))

        if not Customer.objects.filter(user=user).exists():
            raise PermissionDenied("You are not authorized to cancel orders.")

        try:
            order = Order.objects.get(id=order_id, customer=user.customer)
        except Order.DoesNotExist:
            raise ValidationError({"error": "Order not found or does not belong to you."})

        if order.status != "Pending":
            raise ValidationError({"error": f"Cannot cancel the order with status '{order.status}'."})

        with transaction.atomic():
            order.product.available += order.quantity
            order.product.sold -= order.quantity
            order.status = "Cancelled"
            order.product.save()
            order.save()

        return Response({"success": f"Order {order_id} has been successfully cancelled."})
