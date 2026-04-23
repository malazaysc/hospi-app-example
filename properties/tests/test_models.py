from django.contrib.gis.geos import Point
from django.test import TestCase

from properties.models import Amenity, Property, PropertyImage


class AmenityModelTest(TestCase):
    def test_str(self):
        amenity = Amenity.objects.create(name="WiFi")
        self.assertEqual(str(amenity), "WiFi")

    def test_unique_name(self):
        Amenity.objects.create(name="Pool")
        with self.assertRaises(Exception):
            Amenity.objects.create(name="Pool")


class PropertyModelTest(TestCase):
    def setUp(self):
        self.prop = Property.objects.create(
            name="Test Apartment",
            description="A nice place",
            property_type="apartment",
            address="123 Main St",
            city="New York",
            country="USA",
            location=Point(-74.006, 40.7128, srid=4326),
            bedrooms=2,
            bathrooms=1.5,
            max_guests=4,
            base_price_per_night=150.00,
        )

    def test_str(self):
        self.assertEqual(str(self.prop), "Test Apartment")

    def test_latitude_longitude(self):
        self.assertAlmostEqual(self.prop.latitude, 40.7128, places=4)
        self.assertAlmostEqual(self.prop.longitude, -74.006, places=3)

    def test_primary_image_returns_primary(self):
        PropertyImage.objects.create(
            property=self.prop, image_url="https://example.com/1.jpg", is_primary=False
        )
        primary = PropertyImage.objects.create(
            property=self.prop, image_url="https://example.com/2.jpg", is_primary=True
        )
        self.assertEqual(self.prop.primary_image, primary)

    def test_primary_image_fallback(self):
        img = PropertyImage.objects.create(
            property=self.prop, image_url="https://example.com/1.jpg", is_primary=False
        )
        self.assertEqual(self.prop.primary_image, img)

    def test_primary_image_none(self):
        self.assertIsNone(self.prop.primary_image)

    def test_amenities_m2m(self):
        wifi = Amenity.objects.create(name="WiFi")
        pool = Amenity.objects.create(name="Pool")
        self.prop.amenities.set([wifi, pool])
        self.assertEqual(self.prop.amenities.count(), 2)
