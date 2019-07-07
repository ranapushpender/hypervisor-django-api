from django.db import models

# Create your models here.
class IsoModel(models.Model):
    name = models.CharField(max_length=200)
    extension = models.CharField(max_length=20)
    size = models.IntegerField()
    file = models.FileField(default='default.iso')

    def __str__(self):
        return self.name
