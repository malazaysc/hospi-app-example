from django.db import models


class Booking(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("pending", "Pending"),
        ("cancelled", "Cancelled"),
    ]

    property = models.ForeignKey(
        "properties.Property", on_delete=models.CASCADE, related_name="bookings"
    )
    check_in = models.DateField()
    check_out = models.DateField()
    guest_name = models.CharField(max_length=255, blank=True)
    guest_email = models.EmailField(blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["check_in"]

    def __str__(self):
        return f"{self.property.name}: {self.check_in} - {self.check_out}"
