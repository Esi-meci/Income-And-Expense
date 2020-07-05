from django.db import models
from authentication.models import User
from django.utils import timezone
# Create your models here.

class Expense(models.Model):

    CATEGORY_OPTIONS=[
        ('ONLINE_SERVICES','ONLINE_SERVICES'),
        ('TRAVEL','TRAVEL'),
        ('FOOD','FOOD'),
        ('RENT','RENT'),
        ('OTHERS','OTHERS'),
    ]
    category=models.CharField(choices=CATEGORY_OPTIONS, max_length=255) 
    amount=models.DecimalField(max_length=255, max_digits=10, decimal_places=2)
    description=models.TextField() 
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False, blank=False, default=timezone.now)

    class Meta:
        ordering :['-date']

    def __str__(self):
        return str(self.owner)+ "'s expense"