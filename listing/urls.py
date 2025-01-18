from django.urls import path, include
from rest_framework.routers import DefaultRouter
from listing.views import CategoryViewSet

router = DefaultRouter()
router.register('all-category', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
