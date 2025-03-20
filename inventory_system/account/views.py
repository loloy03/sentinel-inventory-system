from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

# Add this new import for your custom form
# You'll need to create forms.py with CustomLoginForm as we discussed
from .forms import CustomLoginForm

# Create your views here.
@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html')

# Add this new login view
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to dashboard after login
    else:
        form = CustomLoginForm()
    
    return render(request, 'account/login.html', {'form': form})