from django.shortcuts import render

# Create your views here.
def release_form(request):
    return render(request, 'release_form/release_form.html')