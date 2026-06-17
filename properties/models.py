from django.db import models
from django.conf import settings
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
# Try Cloudinary, fall back to local ImageField
try:
    from cloudinary_storage.fields import CloudinaryField  # Cloudinary integration
except Exception:
    from django.db.models import ImageField as CloudinaryField

# Use the configured user model
User = settings.AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Property(models.Model):
    # “business status” – rent vs sale
    LISTING_STATUS_CHOICES = (
        ('rent', 'For Rent'),
        ('sale', 'For Sale'),
    )

    # “workflow status” – approval / availability
    WORKFLOW_STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('available', 'Available'),
        ('rented', 'Rented'),
    ]

    # Core fields (combined)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    description = models.TextField(
        blank=True,
        default="Property listed on HouseFinder Mombasa"
    )

    # Financial / listing info
    price = models.DecimalField(max_digits=12, decimal_places=2)
    listing_status = models.CharField(
        max_length=10,
        choices=LISTING_STATUS_CHOICES,
        default='rent'
    )
    workflow_status = models.CharField(
        max_length=20,
        choices=WORKFLOW_STATUS_CHOICES,
        default='pending'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='properties'
    )

    # Location
    location = models.CharField(max_length=200)
    lat = models.FloatField()   # Google Maps
    lng = models.FloatField()

    # Property details
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    size = models.IntegerField(help_text="Square meters", default=0)
    property_type = models.CharField(max_length=50, default='Apartment')

    # Images
    cover_image = CloudinaryField('property_covers/', blank=True)

    # Relationships
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties'
    )

    # Flags / analytics
    approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing_status', 'approved', 'is_featured']),
        ]

    def save(self, *args, **kwargs):
        # Generate slug automatically from title
        if not self.slug:
            self.slug = slugify(self.title)

        # Keep approved flag in sync with workflow_status if you want:
        # approved == True when workflow_status is approved or available
        if self.workflow_status in ['approved', 'available']:
            self.approved = True
        else:
            self.approved = False

        super().save(*args, **kwargs)

    # Permissions
    def can_edit(self, user):
        """Check if user can update this property."""
        return (
            user.is_authenticated and
            (user == self.manager or getattr(user, 'is_manager', lambda: False)() or user.is_superuser)
        )

    def can_delete(self, user):
        return self.can_edit(user)

    # Main image for templates
    @property
    def main_image_url(self):
        """
        Use first related image if exists, otherwise cover_image,
        otherwise None.
        """
        if self.images.exists():
            return self.images.first().image.url
        if self.cover_image:
            try:
                return self.cover_image.url
            except Exception:
                return None
        return None

    def __str__(self):
        return f"{self.title} - KSh {self.price:,}"


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = CloudinaryField('property_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.property.title} - {self.caption[:30] or 'Image'}"


class Inquiry(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='inquiries'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry for {self.property.title} by {self.user.username}"

class SavedProperty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_properties')
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'property')
    
    def __str__(self):
        return f"{self.user.username} saved {self.property.title}"
