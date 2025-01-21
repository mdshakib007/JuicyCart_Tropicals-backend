from django.db import models
from django.template.defaultfilters import slugify
from shop.models import Shop

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True , blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop')
    name = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='images/mangoes/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    available = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)
    about = models.TextField()

    def __str__(self):
        return f"{self.name}"

