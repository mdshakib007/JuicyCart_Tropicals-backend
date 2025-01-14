from django.shortcuts import render
from users.serializers import SellerRegistrationSerializer
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

class SellerRegistrationAPIView(APIView):
    serializer_class = SellerRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response("done")
            
        return Response(serializer.errors)
