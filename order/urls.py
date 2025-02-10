from django.urls import path, include
from order.views import OrderViewSet, CancelOrderAPIView, ChangeOrderStatusAPIView, PaymentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('list', OrderViewSet, basename='order')
router.register('payment', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('cancel/', CancelOrderAPIView.as_view(), name='cancel_order'),
    path('change/', ChangeOrderStatusAPIView.as_view(), name='change_order_status'),
]
