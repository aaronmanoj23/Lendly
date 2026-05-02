from decimal import Decimal

from django.conf import settings
from django.db import models


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        PAID = "paid", "Paid"
        CANCELED = "canceled", "Canceled"
        COMPLETED = "completed", "Completed"

    listing = models.ForeignKey(
        "listings.Listing", on_delete=models.CASCADE, related_name="bookings"
    )
    renter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    message = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def num_days(self) -> int:
        return max((self.end_date - self.start_date).days + 1, 1)

    def compute_total(self) -> Decimal:
        return (self.listing.price_per_day * self.num_days) + self.listing.deposit

    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = self.compute_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking #{self.pk} - {self.listing.title}"
