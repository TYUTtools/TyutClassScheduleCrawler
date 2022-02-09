from django.db import models

# Create your models here.


class Class_Schedule(models.Model):
    s_bjh = models.CharField(max_length=16)
    s_xnxq = models.CharField(max_length=16)
    s_schedule = models.TextField()