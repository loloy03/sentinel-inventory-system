from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.urls import reverse # Can be used with redirect: redirect(reverse('...'))

# Assuming forms.py has CustomLoginForm, likely inheriting from AuthenticationForm
from .forms import CustomLoginForm

def login_view(request):
    if request.user.is_authenticated:
        # Ensure 'forms:dashboard' is the correct URL name for your dashboard
        return redirect('forms:dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            # This assumes CustomLoginForm inherits AuthenticationForm
            user = form.get_user()
            login(request, user)
             # Ensure 'forms:dashboard' is the correct URL name
            return redirect('forms:dashboard')
    else: # GET request
        form = CustomLoginForm(request=request) # Pass request if form needs it

    return render(request, 'account/login.html', {'form': form})

# A separate dashboard view would typically look like this:
# from django.contrib.auth.decorators import login_required
#
# @login_required
# def dashboard_view(request):
#     # Your dashboard logic
#     return render(request, 'account/dashboard.html') # Example template name