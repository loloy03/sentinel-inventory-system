from django.db import models

# Create your models here.
class ReleasedStock(models.Model):
    warehouse_id = models.CharField(max_length=100, blank=True, primary_key=True)
    production_code = models.CharField(max_length=100)
    date = models.DateField()
    product = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    item_code = models.CharField(max_length=100)
    quantity = models.IntegerField()
    pallet_position = models.CharField(max_length=50)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.production_code} - {self.product} ({self.color})"
