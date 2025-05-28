from django.db import models
from accounts.models import Profile

class Meat(models.Model):
    MEAT_TYPE_CHOICES = (
        ('beef', 'Beef'),
        ('pork', 'Pork'),
        ('chicken', 'Chicken'),
        ('lamb', 'Lamb'),
    )
    company = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'company'})
    meat_type = models.CharField(max_length=20, choices=MEAT_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    date_added = models.DateField(auto_now_add=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.meat_type} ({self.quantity}kg) - {self.company.company_name}"
