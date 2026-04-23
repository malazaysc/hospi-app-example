import json

from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse

from properties.models import Amenity, Property, PropertyImage


class PropertyListViewTest(TestCase):
    def test_loads(self):
        response = self.client.get(reverse("properties:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hospi")


class PropertySearchViewTest(TestCase):
    def setUp(self):
        self.ny_prop = Property.objects.create(
            name="NYC Apartment",
            property_type="apartment",
            address="123 Broadway",
            city="New York",
            country="USA",
            location=Point(-74.006, 40.7128, srid=4326),
            bedrooms=2,
            bathrooms=1,
            max_guests=4,
            base_price_per_night=200,
        )
        self.paris_prop = Property.objects.create(
            name="Paris Loft",
            property_type="loft",
            address="10 Rue de Rivoli",
            city="Paris",
            country="France",
            location=Point(2.3522, 48.8566, srid=4326),
            bedrooms=1,
            bathrooms=1,
            max_guests=2,
            base_price_per_night=150,
        )
        PropertyImage.objects.create(
            property=self.ny_prop,
            image_url="https://example.com/ny.jpg",
            is_primary=True,
        )

    def test_search_by_bounds_finds_nyc(self):
        response = self.client.get(
            reverse("properties:search"),
            {"south": "40.0", "west": "-75.0", "north": "41.0", "east": "-73.0"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NYC Apartment")
        self.assertNotContains(response, "Paris Loft")

    def test_search_by_bounds_finds_paris(self):
        response = self.client.get(
            reverse("properties:search"),
            {"south": "48.0", "west": "2.0", "north": "49.0", "east": "3.0"},
        )
        self.assertContains(response, "Paris Loft")
        self.assertNotContains(response, "NYC Apartment")

    def test_filter_by_property_type(self):
        response = self.client.get(
            reverse("properties:search"),
            {
                "south": "-90", "west": "-180", "north": "90", "east": "180",
                "property_type": "loft",
            },
        )
        self.assertContains(response, "Paris Loft")
        self.assertNotContains(response, "NYC Apartment")

    def test_filter_by_min_bedrooms(self):
        response = self.client.get(
            reverse("properties:search"),
            {
                "south": "-90", "west": "-180", "north": "90", "east": "180",
                "min_bedrooms": "2",
            },
        )
        self.assertContains(response, "NYC Apartment")
        self.assertNotContains(response, "Paris Loft")

    def test_filter_by_price_range(self):
        response = self.client.get(
            reverse("properties:search"),
            {
                "south": "-90", "west": "-180", "north": "90", "east": "180",
                "max_price": "175",
            },
        )
        self.assertContains(response, "Paris Loft")
        self.assertNotContains(response, "NYC Apartment")

    def test_filter_by_amenities(self):
        wifi = Amenity.objects.create(name="WiFi")
        self.ny_prop.amenities.add(wifi)
        response = self.client.get(
            reverse("properties:search"),
            {
                "south": "-90", "west": "-180", "north": "90", "east": "180",
                "amenities": [str(wifi.id)],
            },
        )
        self.assertContains(response, "NYC Apartment")
        self.assertNotContains(response, "Paris Loft")


class PropertyMarkersViewTest(TestCase):
    def setUp(self):
        Property.objects.create(
            name="Berlin Studio",
            property_type="studio",
            address="Unter den Linden 1",
            city="Berlin",
            country="Germany",
            location=Point(13.405, 52.52, srid=4326),
            bedrooms=1,
            bathrooms=1,
            max_guests=2,
            base_price_per_night=80,
        )

    def test_returns_json(self):
        response = self.client.get(
            reverse("properties:markers"),
            {"south": "52.0", "west": "13.0", "north": "53.0", "east": "14.0"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Berlin Studio")
        self.assertIn("lat", data[0])
        self.assertIn("lng", data[0])

    def test_no_results_outside_bounds(self):
        response = self.client.get(
            reverse("properties:markers"),
            {"south": "0", "west": "0", "north": "1", "east": "1"},
        )
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)


class PropertyDetailViewTest(TestCase):
    def setUp(self):
        self.prop = Property.objects.create(
            name="Rome Villa",
            property_type="villa",
            address="Via del Corso 1",
            city="Rome",
            country="Italy",
            location=Point(12.4964, 41.9028, srid=4326),
            bedrooms=3,
            bathrooms=2,
            max_guests=6,
            base_price_per_night=300,
        )

    def test_loads(self):
        response = self.client.get(
            reverse("properties:detail", kwargs={"pk": self.prop.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rome Villa")
        self.assertContains(response, "$300")

    def test_404_for_missing(self):
        response = self.client.get(
            reverse("properties:detail", kwargs={"pk": 99999})
        )
        self.assertEqual(response.status_code, 404)
