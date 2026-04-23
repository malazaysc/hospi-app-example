from datetime import date

from django.contrib.gis.geos import Point
from django.test import TestCase

from bookings.models import Booking
from properties.models import Property


class BookingModelTest(TestCase):
    def setUp(self):
        self.prop = Property.objects.create(
            name="Test Property",
            property_type="apartment",
            address="1 Test St",
            city="London",
            country="UK",
            location=Point(-0.1278, 51.5074, srid=4326),
            bedrooms=1,
            bathrooms=1,
            max_guests=2,
            base_price_per_night=100,
        )

    def test_str(self):
        booking = Booking.objects.create(
            property=self.prop,
            check_in=date(2026, 6, 1),
            check_out=date(2026, 6, 5),
            guest_name="John Doe",
            total_price=400,
        )
        self.assertIn("Test Property", str(booking))

    def test_default_status(self):
        booking = Booking.objects.create(
            property=self.prop,
            check_in=date(2026, 7, 1),
            check_out=date(2026, 7, 3),
        )
        self.assertEqual(booking.status, "confirmed")

    def test_cascade_delete(self):
        Booking.objects.create(
            property=self.prop,
            check_in=date(2026, 8, 1),
            check_out=date(2026, 8, 5),
        )
        self.prop.delete()
        self.assertEqual(Booking.objects.count(), 0)
