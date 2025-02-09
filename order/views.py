from django.shortcuts import render, redirect
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
from django.contrib.auth.models import User
from sslcommerz_lib import SSLCOMMERZ
import random 
import string
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


def unique_trax_id_generator(size=15, chars=string.ascii_uppercase + string.ascii_lowercase):
    return "".join(random.choice(chars) for _ in range(size))


class SpecificOrder(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        order_id = request.query_params.get('order_id')
        shop_id = request.query_params.get('shop_id')
        customer_id = request.query_params.get('customer_id')

        if order_id:
            queryset = queryset.filter(id=order_id)
        if shop_id:
            queryset = queryset.filter(product__shop__id=shop_id)
        if customer_id:
            queryset = queryset.filter(customer=customer_id)
        
        return queryset


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    filter_backends = [SpecificOrder]


class PlaceOrderAPIView(views.APIView):
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        user_id = request.data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError({"error" : "User not found."})

        if not Customer.objects.filter(user=user).exists():
            raise PermissionDenied("You do not have access to buy any product.")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError({"error": "Invalid product ID."})

        if product.available < int(quantity):
            raise ValidationError({"error": "Not enough stock available."})


        cancel_url = f"mdshakib007.github.io/JuicyCart_Tropicals-Frontend/single_product.html?product_id={product_id}"

        # sslcommerz
        settings = { 'store_id': 'juicy67a80e7052c5e', 'store_pass': 'juicy67a80e7052c5e@ssl', 'issandbox': True }
        sslcz = SSLCOMMERZ(settings)
        post_body = {}
        post_body['total_amount'] = product.price * int(quantity)
        post_body['currency'] = "BDT"
        post_body['tran_id'] = unique_trax_id_generator()
        post_body['success_url'] = f"https://juicycart-tropicals.onrender.com/order/payment/{post_body['tran_id']}/success/"
        post_body['fail_url'] = "https://juicycart-tropicals.onrender.com/order/failed/"
        post_body['cancel_url'] = cancel_url
        post_body['emi_option'] = 0
        post_body['cus_name'] = user.username
        post_body['cus_email'] = user.email
        post_body['cus_phone'] = "01XXXXXXXXX"
        post_body['cus_add1'] = user.customer.full_address
        post_body['cus_city'] = "Dhaka"
        post_body['cus_country'] = "Bangladesh"
        post_body['shipping_method'] = "NO"
        post_body['multi_card_name'] = ""
        post_body['num_of_item'] = 1
        post_body['product_name'] = product.name
        post_body['product_category'] = product.category
        post_body['product_profile'] = "general"


        response = sslcz.createSession(post_body)  # API response

        return Response({"gateway_url": response['GatewayPageURL']})



@csrf_exempt
def payment_success(request, trax_id):
    product_id = request.GET.get('product_id')
    quantity = request.GET.get('quantity')
    user_id = request.GET.get('user_id')

    if not (product_id and quantity and user_id):
        return Response({"error": "Missing required parameters."})

    try:
        quantity = int(quantity)
    except ValueError:
        return Response({"error": "Quantity must be an integer."})

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."})

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."})

    if not hasattr(user, 'customer'):
        return Response({"error": "User is not associated with a customer."})

    with transaction.atomic():
        if product.available < quantity:
            return Response({"error": "Insufficient stock available."})
        product.available -= quantity
        product.sold += quantity
        product.save()

        order = Order.objects.create(
            product=product,
            customer=user.customer,
            quantity=quantity,
            total_price=product.price * quantity,
        )

    serializer = OrderSerializer(order)
    return Response({"success" : "Your order has been placed successfully!"})

def order_failed(request):
    return Response({"error": "Payment failed."})


class CancelOrderAPIView(views.APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        order_id = int(request.data.get('order_id'))

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError({"error" : "User not found."})

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


class ChangeOrderStatusAPIView(views.APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        customer_id = request.data.get('customer_id')
        order_id = request.data.get('order_id')
        order_status = request.data.get('order_status')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError({"error" : "user not found."})
        
        try:
            customer_user = User.objects.get(id=customer_id)
        except User.DoesNotExist:
            raise ValidationError({"error" : "does not exists"})
        
        if not Customer.objects.filter(user=customer_user).exists():
            raise PermissionDenied("invalid customer id.")

        if not Seller.objects.filter(user=user).exists():
            raise PermissionDenied("seller does not exists.")

        try:
            order = Order.objects.get(id=order_id, customer=customer_user.customer)
        except Order.DoesNotExist:
            raise ValidationError({"error": "Order not found or does not belong to this customer."})

        if order.status != "Pending":
            raise ValidationError({"error": f"Cannot change the order with status '{order.status}'."})

        if order_status == "Cancelled":
            with transaction.atomic():
                order.product.available += order.quantity
                order.product.sold -= order.quantity
                order.status = "Cancelled"
                order.product.save()
                order.save()

            return Response({"success": f"Order {order_id} has been successfully cancelled."})
        
        else:
            with transaction.atomic():
                order.status = order_status
                order.save()

            return Response({"success" : "order status updated."})