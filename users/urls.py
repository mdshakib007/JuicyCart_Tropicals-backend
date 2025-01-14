from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import SellerRegistrationAPIView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('register/seller/', SellerRegistrationAPIView.as_view(), name='seller_register'),
]
