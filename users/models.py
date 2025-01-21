from django.db import models
from django.contrib.auth.models import User


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller', primary_key=True)
    image = models.ImageField(upload_to='images/default/', default='images/default/default_seller.png')
    # shop = models.OneToOneField()
    mobile_no = models.CharField(max_length=16)
    full_address = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.user.username}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer', primary_key=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    image = models.ImageField(upload_to='images/default/', default='images/default/default_customer.png')
    full_address = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.user.username}"
