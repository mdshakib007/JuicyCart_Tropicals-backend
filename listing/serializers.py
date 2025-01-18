from rest_framework import serializers
from listing.models import Category, Mango


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class MangoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mango
        fields = '__all__'