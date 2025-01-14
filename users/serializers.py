from rest_framework import serializers
from django.contrib.auth.models import User

class SellerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
    
    def save(self):
        username = self.validated_data['username']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        email = self.validated_data['email']
        password = self.validated_data['password']

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email', "This Email Already Exists!"})
        
        account = User(username=username, first_name=first_name, last_name=last_name, email=email)
        account.set_password(password)
        account.save()

        return account