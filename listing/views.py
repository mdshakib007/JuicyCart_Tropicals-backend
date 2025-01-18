from django.shortcuts import render
from listing.models import Category, Mango
from listing.serializers import CategorySerializer, MangoSerializer
from rest_framework import viewsets


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(id = category_id)

        return queryset


class MangoViewSet(viewsets.ModelViewSet):
    queryset = Mango.objects.all()