from django.db import models
from django.conf import settings
try:
    from cloudinary_storage.fields import CloudinaryField  # Cloudinary integration
except Exception:
    # Fallback for environments without cloudinary_storage installed: use ImageField
    from django.db.models import ImageField as CloudinaryField
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Property(models.Model):
    STATUS_CHOICES = (
        ('rent', 'For Rent'),
        ('sale', 'For Sale'),
    )
    
    # object attributes / table fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, default="Property listed on HouseFinder Mombasa")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='rent')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='properties')
    location = models.CharField(max_length=200)
    lat = models.FloatField()  # Google Maps
    lng = models.FloatField()
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    
    # Cloudinary images (multiple)
    cover_image = CloudinaryField('property_covers/', blank=True)
    
    # relationships
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    
    approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status', 'approved', 'is_featured'])]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    # Permissions
    def can_edit(self, user):
        '''check if user can update this property'''
        return user == self.manager or user.is_manager() or user.is_superuser
    
    def can_delete(self, user):
        return user == self.manager or user.is_manager() or user.is_superuser
    
    # Main image for templates
    @property
    def main_image(self):
        return self.images.first().image.url if self.images.exists() else None
    
    def __str__(self):
        return f"{self.title} - KSh {self.price:,}"

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField('property_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.property.title} - {self.caption[:30]}"

class Inquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Inquiry for {self.property.title} by {self.user.username}"

# class Commission(models.Model):
#     property = models.ForeignKey(Property, on_delete=models.CASCADE)
#     rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.05)  # 5%
#     amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     date_added = models.DateTimeField(auto_now_add=True)
    
#     def save(self, *args, **kwargs):
#         if self.property.price and self.rate:
#             self.amount = self.property.price * self.rate
#         super().save(*args, **kwargs)
