from rest_framework import serializers
from .models import IsoModel

class IsoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IsoModel
        fields = ('id','name','extension','size','file')