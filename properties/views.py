import json
from django.contrib.gis.geos import Polygon
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import Amenity, Property


@require_GET
def property_list(request):
    """Main page with map and property list."""
    amenities = Amenity.objects.all()
    property_types = Property.PROPERTY_TYPES
    return render(
        request,
        "properties/property_list.html",
        {
            "amenities": amenities,
            "property_types": property_types,
        },
    )


@require_GET
def property_search(request):
    """HTMX endpoint: returns property cards filtered by map bounds and filters."""
    qs = Property.objects.prefetch_related("images", "amenities")

    # Filter by map bounds
    south = request.GET.get("south")
    west = request.GET.get("west")
    north = request.GET.get("north")
    east = request.GET.get("east")

    if all([south, west, north, east]):
        try:
            bbox = Polygon.from_bbox((
                float(west), float(south), float(east), float(north)
            ))
            bbox.srid = 4326
            qs = qs.filter(location__within=bbox)
        except (ValueError, TypeError):
            pass

    # Filter by property type
    property_type = request.GET.get("property_type")
    if property_type:
        qs = qs.filter(property_type=property_type)

    # Filter by bedrooms
    min_bedrooms = request.GET.get("min_bedrooms")
    if min_bedrooms:
        try:
            qs = qs.filter(bedrooms__gte=int(min_bedrooms))
        except ValueError:
            pass

    # Filter by price range
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        try:
            qs = qs.filter(base_price_per_night__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            qs = qs.filter(base_price_per_night__lte=float(max_price))
        except ValueError:
            pass

    # Filter by max guests
    min_guests = request.GET.get("min_guests")
    if min_guests:
        try:
            qs = qs.filter(max_guests__gte=int(min_guests))
        except ValueError:
            pass

    # Filter by amenities
    amenities = request.GET.getlist("amenities")
    if amenities:
        for amenity_id in amenities:
            qs = qs.filter(amenities__id=amenity_id)

    properties = qs.distinct()[:50]

    return render(
        request,
        "properties/partials/property_cards.html",
        {"properties": properties},
    )


@require_GET
def property_markers(request):
    """JSON endpoint: returns markers for the map based on current bounds."""
    qs = Property.objects.all()

    south = request.GET.get("south")
    west = request.GET.get("west")
    north = request.GET.get("north")
    east = request.GET.get("east")

    if all([south, west, north, east]):
        try:
            bbox = Polygon.from_bbox((
                float(west), float(south), float(east), float(north)
            ))
            bbox.srid = 4326
            qs = qs.filter(location__within=bbox)
        except (ValueError, TypeError):
            pass

    # Apply same filters as search
    property_type = request.GET.get("property_type")
    if property_type:
        qs = qs.filter(property_type=property_type)

    min_bedrooms = request.GET.get("min_bedrooms")
    if min_bedrooms:
        try:
            qs = qs.filter(bedrooms__gte=int(min_bedrooms))
        except ValueError:
            pass

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        try:
            qs = qs.filter(base_price_per_night__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            qs = qs.filter(base_price_per_night__lte=float(max_price))
        except ValueError:
            pass

    min_guests = request.GET.get("min_guests")
    if min_guests:
        try:
            qs = qs.filter(max_guests__gte=int(min_guests))
        except ValueError:
            pass

    amenities = request.GET.getlist("amenities")
    if amenities:
        for amenity_id in amenities:
            qs = qs.filter(amenities__id=amenity_id)

    markers = []
    for p in qs.distinct()[:50]:
        markers.append({
            "id": p.id,
            "lat": p.latitude,
            "lng": p.longitude,
            "name": p.name,
            "price": str(p.base_price_per_night),
            "type": p.get_property_type_display(),
        })

    return JsonResponse(markers, safe=False)


@require_GET
def property_detail(request, pk):
    """Property detail page."""
    prop = get_object_or_404(
        Property.objects.prefetch_related("images", "amenities", "bookings"),
        pk=pk,
    )
    confirmed_bookings = prop.bookings.filter(status="confirmed").order_by("check_in")
    return render(
        request,
        "properties/property_detail.html",
        {
            "property": prop,
            "bookings": confirmed_bookings,
        },
    )
