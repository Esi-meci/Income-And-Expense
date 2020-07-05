from rest_framework import serializers
from .models import Income

class IncomeSerializer(serializers.ModelSerializer):
    date=serializers.DateTimeField(read_only=True)
    class Meta:
        model = Income
        fields = ['id','date','description','amount','source']