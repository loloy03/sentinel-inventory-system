from django.urls import path 
from . import views

app_name='recieve_form'

urlpatterns = [
    path('', views.recieve_form, name='recieve_form'),
]

