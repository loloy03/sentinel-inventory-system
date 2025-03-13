from django.shortcuts import render

# Create your views here.
def recieve_form(request):
    return render(request, 'recieve_form/recieve_form.html')