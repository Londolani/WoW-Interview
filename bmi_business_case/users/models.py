from django.db import models

# Create your models here.
class User(models.Model):
    average = models.IntegerField()
    participants = models.IntegerField()
    overnight = models.IntegerField()
    name = models.CharField(max_length=156)

    def __str__(self):
        return str(self.name)