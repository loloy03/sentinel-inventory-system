from django.shortcuts import render

# Create your views here.
def warehouse_map(request):
    return render(request, 'warehouse_layout/warehouse_layout.html')