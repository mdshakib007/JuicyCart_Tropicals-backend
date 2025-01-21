from django.urls import path, include
from rest_framework.routers import DefaultRouter
from listing.views import CategoryViewSet, ProductViewSet, AddProductAPIView

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('product/add/', AddProductAPIView.as_view(), name='add_product'),
]
