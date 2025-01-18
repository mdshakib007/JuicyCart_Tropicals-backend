from django.db import models
from django.template.defaultfilters import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True , blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"


class Mango(models.Model):
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to='images/mangoes/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    available = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)
    about = models.TextField()

    def __str__(self):
        return f"{self.name}"

