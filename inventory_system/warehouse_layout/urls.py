from django.urls import path
from . import views

app_name='warehouse_layout'

urlpatterns = [
    path('', views.warehouse_map, name='warehouse_map'),
]