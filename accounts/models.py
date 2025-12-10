from django.contrib.auth.models import AbstractUser
from django.db import models
try:
    from cloudinary_storage.fields import CloudinaryField
except Exception:
    from django.db.models import ImageField as CloudinaryField

# Create your models here. email, password fields will come from our abstract user 
class User(AbstractUser):
    # define our user roles (adapted for HouseFinder Mombasa)
    USER_TYPE_CHOICES = (
        ('renter', 'Renter/Buyer'),
        ('manager', 'Property Manager'),
        ('admin', 'Administrator'),
    )
    
    # table columns 
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='renter')
    profile_image = CloudinaryField('profile_images/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    
    # Mombasa-specific fields (kept for functionality)
    phone = models.CharField(max_length=15, blank=True)
    national_id = CloudinaryField('national_ids/', blank=True)
    kra_pin = models.CharField(max_length=20, blank=True)
    verified = models.BooleanField(default=False)
    
    # methods they can access 
    def __str__(self):
        return f"{self.username} - {self.email}"
    
    def is_manager(self):
        return self.user_type == 'manager'
    
    def is_renter(self):
        return self.user_type == 'renter'
    
    def is_admin(self):
        return self.user_type == 'admin'
