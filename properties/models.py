from django.contrib.gis.db import models


class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "amenities"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Property(models.Model):
    PROPERTY_TYPES = [
        ("apartment", "Apartment"),
        ("house", "House"),
        ("condo", "Condo"),
        ("villa", "Villa"),
        ("studio", "Studio"),
        ("townhouse", "Townhouse"),
        ("cottage", "Cottage"),
        ("loft", "Loft"),
        ("penthouse", "Penthouse"),
        ("bungalow", "Bungalow"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    location = models.PointField(srid=4326)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1)
    max_guests = models.PositiveIntegerField()
    base_price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    amenities = models.ManyToManyField(Amenity, blank=True, related_name="properties")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "properties"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def latitude(self):
        return self.location.y

    @property
    def longitude(self):
        return self.location.x


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="images"
    )
    image_url = models.URLField()
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.property.name}"
