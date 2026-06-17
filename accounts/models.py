from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField
from properties.models import Property

try:
    from cloudinary_storage.fields import CloudinaryField
except Exception:
    from django.db.models import ImageField as CloudinaryField

# Create your models here. email, password fields will come from our abstract user 
class User(AbstractUser):
    # define our user roles 
    USER_TYPE_CHOICES = (
        ('renter', 'Renter/Buyer'),
        ('manager', 'Property Manager'),
        ('admin', 'Administrator'),
    )
    
    # table columns 

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='renter')
    profile_image = CloudinaryField('profile_images/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    kra_pin = models.CharField(max_length=20, blank=True, null=True)
    # national_id = models.CharField(max_length=20, blank=True, null=True)
    national_id = CloudinaryField('national_ids/', null=True, blank=True)
    approval_status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    is_verified = models.BooleanField(default=False)
    
    # kra_pin = models.CharField(max_length=20, blank=True)
    # verified = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.user_type == 'regular':
            self.kra_pin = ''
            self.national_id = ''
            self.approval_status = 'approved'
            self.is_verified = True
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.username} - {self.email}"

    def is_manager(self):
        return self.user_type == 'manager'

    def is_renter(self):
        return self.user_type == 'renter'

    def is_admin(self):
        return self.user_type == 'admin'

    # Mombasa-specific fields - kept for functionality



class ScheduledVisit(models.Model):
    renter = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE)
    visit_date = models.DateTimeField()

    def __str__(self):
        return f"{self.renter.username} - {self.property}"
