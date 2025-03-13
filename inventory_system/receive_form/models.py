from django.db import models

# Create your models here.
class ReceivedStock(models.Model):
    production_id = models.CharField(max_length=100)
    date = models.DateField()
    product = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    item_code = models.CharField(max_length=100)
    quantity = models.IntegerField()
    status = models.CharField(max_length=50, default="RECEIVED")

    def __str__(self):
        return f"{self.production_id} - {self.product} ({self.color})"