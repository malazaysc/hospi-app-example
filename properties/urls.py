from django.urls import path
from . import views

app_name = "properties"

urlpatterns = [
    path("", views.property_list, name="list"),
    path("search/", views.property_search, name="search"),
    path("markers/", views.property_markers, name="markers"),
    path("property/<int:pk>/", views.property_detail, name="detail"),
]
