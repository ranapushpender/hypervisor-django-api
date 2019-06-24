from django.db import models

class VM(models.Model):
    name = models.CharField(max_length=30)
    os = models.CharField(max_length=30)
    image = models.ImageField(default='default.png',blank=True)

    def __str__(self):
        return self.name