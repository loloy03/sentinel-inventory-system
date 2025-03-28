from django.urls import path
from . import views

app_name = "forms"

urlpatterns = [
    path("", views.receive_form, name="receive_form"),
    path("release", views.release_form, name="release_form"),
    path("warehouse/outside/", views.warehouse_outside, name="warehouse_outside"),
    path("warehouse/area/", views.warehouse_area, name="warehouse_area"),
    path("search/key", views.search_key, name="search_key"),
    path("search/pallet/", views.search_pallet, name="search_pallet"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('history/', views.history_view, name='history'),
]
