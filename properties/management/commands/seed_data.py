import random
from datetime import datetime, timedelta

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from faker import Faker

from bookings.models import Booking
from properties.models import Amenity, Property, PropertyImage

fake = Faker()

AMENITY_NAMES = [
    "WiFi", "Air Conditioning", "Heating", "Kitchen", "Washer",
    "Dryer", "Parking", "Pool", "Gym", "Balcony", "Garden",
    "Fireplace", "TV", "Dishwasher", "Microwave", "Coffee Maker",
    "Pet Friendly", "Smoking Allowed", "Elevator", "Security",
]

CITIES = [
    {"name": "New York", "lat": 40.7128, "lon": -74.0060, "country": "USA"},
    {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "country": "USA"},
    {"name": "London", "lat": 51.5074, "lon": -0.1278, "country": "UK"},
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522, "country": "France"},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503, "country": "Japan"},
    {"name": "Sydney", "lat": -33.8688, "lon": 151.2093, "country": "Australia"},
    {"name": "Barcelona", "lat": 41.3851, "lon": 2.1734, "country": "Spain"},
    {"name": "Amsterdam", "lat": 52.3676, "lon": 4.9041, "country": "Netherlands"},
    {"name": "Berlin", "lat": 52.5200, "lon": 13.4050, "country": "Germany"},
    {"name": "Rome", "lat": 41.9028, "lon": 12.4964, "country": "Italy"},
]

PROPERTY_TYPES = [c[0] for c in Property.PROPERTY_TYPES]


class Command(BaseCommand):
    help = "Seed the database with sample property data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=100, help="Number of properties to create"
        )
        parser.add_argument(
            "--clear", action="store_true", help="Clear existing data before seeding"
        )

    def handle(self, *args, **options):
        count = options["count"]
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            Booking.objects.all().delete()
            PropertyImage.objects.all().delete()
            Property.objects.all().delete()
            Amenity.objects.all().delete()

        # Create amenities
        amenities = []
        for name in AMENITY_NAMES:
            amenity, _ = Amenity.objects.get_or_create(name=name)
            amenities.append(amenity)
        self.stdout.write(f"Created {len(amenities)} amenities")

        # Create properties
        for i in range(count):
            city = random.choice(CITIES)
            prop_type = random.choice(PROPERTY_TYPES)
            bedrooms = random.randint(1, 5)
            bathrooms = round(random.uniform(1, bedrooms + 1), 1)
            max_guests = bedrooms * 2 + random.randint(0, 2)

            base_price = random.uniform(50, 500)
            if prop_type in ("villa", "penthouse"):
                base_price = random.uniform(200, 800)
            elif prop_type == "studio":
                base_price = random.uniform(30, 150)
            if city["name"] in ("New York", "London", "Tokyo"):
                base_price *= random.uniform(1.2, 1.8)

            lat = city["lat"] + random.uniform(-0.1, 0.1)
            lon = city["lon"] + random.uniform(-0.1, 0.1)

            prop = Property.objects.create(
                name=f"{prop_type.title()} in {city['name']}",
                description=fake.text(max_nb_chars=500),
                property_type=prop_type,
                address=fake.street_address(),
                city=city["name"],
                country=city["country"],
                location=Point(lon, lat, srid=4326),
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                max_guests=max_guests,
                base_price_per_night=round(base_price, 2),
                currency="USD",
            )

            # Add random amenities
            selected = random.sample(amenities, random.randint(5, 12))
            prop.amenities.set(selected)

            # Add images
            num_images = random.randint(3, 8)
            for j in range(num_images):
                seed = prop.id * 100 + j
                PropertyImage.objects.create(
                    property=prop,
                    image_url=f"https://picsum.photos/seed/{seed}/800/600",
                    is_primary=(j == 0),
                )

            # Add bookings
            num_bookings = random.randint(0, 5)
            for _ in range(num_bookings):
                days_ahead = random.randint(1, 180)
                check_in = datetime.now().date() + timedelta(days=days_ahead)
                stay = random.randint(2, 7)
                check_out = check_in + timedelta(days=stay)
                Booking.objects.create(
                    property=prop,
                    check_in=check_in,
                    check_out=check_out,
                    guest_name=fake.name(),
                    guest_email=fake.email(),
                    total_price=round(base_price * stay * random.uniform(0.9, 1.1), 2),
                    status=random.choice(["confirmed", "pending", "cancelled"]),
                )

            if (i + 1) % 10 == 0:
                self.stdout.write(f"  Created {i + 1}/{count} properties...")

        total = Property.objects.count()
        bookings = Booking.objects.filter(status="confirmed").count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Done! {total} properties, {bookings} confirmed bookings"
            )
        )
