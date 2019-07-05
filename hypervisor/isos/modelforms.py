from rest_framework import serializers
from .models import IsoModel

class IsoForm(serializers.ModelSerializer):
    class Meta:
        model = IsoModel
        fields = ['name','extension','size']