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
