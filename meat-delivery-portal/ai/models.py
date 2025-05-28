from django.db import models

class DemandForecast(models.Model):
    meat_type = models.CharField(max_length=20)
    forecast_date = models.DateField()
    predicted_demand = models.PositiveIntegerField()
