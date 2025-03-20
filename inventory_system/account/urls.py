from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),  # Add this new path for the login view
]