from django.db import models
from users.models import Seller


class Shop(models.Model):
    owner = models.OneToOneField(Seller, on_delete=models.CASCADE, related_name='owner')
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to='images/shops/', default='images/default/default_mango.png')
    description = models.TextField()
    location = models.CharField(max_length=250)
    hotline = models.CharField(max_length=20, null=True, blank=True, default=None)
    total_sold = models.DecimalField(decimal_places=2, max_digits=12, default=0, null=True, blank=True)
    rank = models.IntegerField(default=0, unique=False)

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        shops = Shop.objects.order_by('-total_sold')
        for index, shop in enumerate(shops, start=1):
            shop.rank = index
            super(Shop, shop).save(update_fields=['rank'])
