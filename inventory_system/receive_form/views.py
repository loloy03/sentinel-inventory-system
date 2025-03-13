from django.shortcuts import render

# Create your views here.
def receive_form(request):
    return render(request, 'receive_form/receive_form.html')