from django.db import models
from authentication.models import User
from django.utils import timezone
# Create your models here.

class Income(models.Model):

    SOURCE_OPTIONS=[
        ('SALARY','SALARY'),
        ('BUSINESS','BUSINESS'),
        ('SIDE_HUSLTE','SIDE_HUSLTE'),
        ('OTHERS','OTHERS'),
    ]
    source=models.CharField(choices=SOURCE_OPTIONS, max_length=255) 
    amount=models.DecimalField(max_length=255, max_digits=10, decimal_places=2)
    description=models.TextField() 
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False, blank=False, default=timezone.now)

    class Meta:
        ordering :['-date']

    def __str__(self):
        return str(self.owner)+ "'s income"