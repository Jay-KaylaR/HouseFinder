from django.db import models
from django.conf import settings
from properties.models import Property

class Commission(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_tx_id = models.CharField(max_length=100, blank=True)
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Commission for {self.property.title} - KSh {self.amount}"
