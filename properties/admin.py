from django.contrib.gis import admin
from .models import Amenity, Property, PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.GISModelAdmin):
    list_display = ["name", "property_type", "city", "country", "base_price_per_night", "bedrooms"]
    list_filter = ["property_type", "city", "country"]
    search_fields = ["name", "address", "city"]
    filter_horizontal = ["amenities"]
    inlines = [PropertyImageInline]


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
