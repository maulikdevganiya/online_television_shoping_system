from django.db import models
from app.models import Product

class Collection(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Draft', 'Draft'),
    )

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CollectionProduct(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='collection_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.collection.title} - {self.product.title}"
