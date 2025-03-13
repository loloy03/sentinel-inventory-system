from django.urls import path 
from . import views

app_name='release_form'

urlpatterns = [
    path('', views.release_form, name='release_form'),
]
