from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import SellerRegistrationAPIView, activate, CustomerRegistrationAPIView, UserLoginAPIView, UserLogoutAPIView, UserViewSet

router = DefaultRouter()
router.register('list', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/seller/', SellerRegistrationAPIView.as_view(), name='seller_register'),
    path('register/customer/', CustomerRegistrationAPIView.as_view(), name='customer_register'),
    path('activate/<uid64>/<token>/', activate, name="activate"),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('logout/', UserLogoutAPIView.as_view(), name='logout'),

]
