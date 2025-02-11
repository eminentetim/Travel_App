from django.db import models
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils.translation import gettext_lazy as _


# Create your models here.
# listings/models.py
class Listing(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    available_from = models.DateField()
    available_to = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    number_of_guests = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.listing.title} ({self.check_in} to {self.check_out})"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')

    def __str__(self):
        return f"{self.user.username} - {self.listing.title} ({self.rating}/5)"
    
class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", _("Payment is on pending",)
        CONFIRMED = "success", _("Payment successful")
        REFUNDED = "refunded", _("Payment refunded")
        REVERSED = "reversed", _("Payment reversed")
        CANCELED = "failed", _("Payment failed/cancelled")

    payment_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    booking_id = models.ForeignKey(
        to=Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=9, choices=Status, default=Status.PENDING)