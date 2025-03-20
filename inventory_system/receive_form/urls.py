from django.urls import path 
from . import views

app_name = 'receive_form'

urlpatterns = [
    path('', views.receive_form, name='receive_form'),
    path('warehouse/layout/', views.warehouse_layout, name='warehouse_layout'),
]