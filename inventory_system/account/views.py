from django.shortcuts import render
# Import the login_required decorator to restrict access to authenticated users
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html')