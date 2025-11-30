from django.db import models
from django.contrib.auth.hashers import make_password


class Admin(models.Model):
    A_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    passw = models.CharField(max_length=25)

    def __str__(self):
        return f"{self.name}"
    
class UserRegister(models.Model):
    name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Hash password before saving
        if not self.pk or "pbkdf2_" not in self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.last_name:
            return f"{self.name} {self.last_name} <{self.email}>"
        return f"{self.name} <{self.email}>"

class Brand(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
    )

    bname = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    bimage = models.ImageField(upload_to='brandimages/')
    b_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="active"
    )

    def __str__(self):
        return self.bname

class Carousel(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    c_title = models.CharField(max_length=255)
    c_link = models.CharField(max_length=255, blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)
    c_status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    c_img = models.ImageField(upload_to='carousel_images/')

    def __str__(self):
        return self.c_title

    class Meta:
        ordering = ['sort_order']  # Orders carousels by sort_order

class Product(models.Model):
    title = models.CharField(max_length=200)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.IntegerField(default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)

    # New fields
    stock = models.IntegerField(default=0)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)

    # Media
    main_image = models.ImageField(upload_to='products/main/')
    thumb_1 = models.ImageField(upload_to='products/thumbs/', blank=True, null=True)
    thumb_2 = models.ImageField(upload_to='products/thumbs/', blank=True, null=True)
    thumb_3 = models.ImageField(upload_to='products/thumbs/', blank=True, null=True)
    thumb_4 = models.ImageField(upload_to='products/thumbs/', blank=True, null=True)

    # We will store the generated HTML description here
    description_html = models.TextField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-calculate final price on save
        if self.original_price is not None:
            discount_amount = (self.original_price * self.discount_percentage) / 100
            self.final_price = self.original_price - discount_amount
        super().save(*args, **kwargs)

class ProductFeature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features')
    feature_text = models.CharField(max_length=255)

    def __str__(self):
        return self.feature_text