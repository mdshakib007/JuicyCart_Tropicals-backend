from django.urls import path, include
from order.views import OrderViewSet, PlaceOrderAPIView, CancelOrderAPIView, ChangeOrderStatusAPIView, order_failed, payment_success
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('list', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('place/', PlaceOrderAPIView.as_view(), name='place_order'),
    path('payment/<int:trax_id>/success/', payment_success, name='payment_success'),
    path('failed/', order_failed, name='order_failed'),
    path('cancel/', CancelOrderAPIView.as_view(), name='cancel_order'),
    path('change/', ChangeOrderStatusAPIView.as_view(), name='change_order_status'),
]
