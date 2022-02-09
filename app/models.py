from django.db import models

# Create your models here.


class Class_Schedule(models.Model):
    s_bjh = models.CharField(max_length=16)
    s_xnxq = models.CharField(max_length=16)
    s_schedule = models.TextField()


class yunlu_class_schedule(models.Model):
    # 专业班级
    bjh = models.CharField(max_length=16)
    # 接下来是每一周的情况，每一周由20个01字符表示，每一个表示一个大节是否有课。
    week1 = models.CharField(max_length=20)
    week2 = models.CharField(max_length=20)
    week3 = models.CharField(max_length=20)
    week4 = models.CharField(max_length=20)
    week5 = models.CharField(max_length=20)
    week6 = models.CharField(max_length=20)
    week7 = models.CharField(max_length=20)
    week8 = models.CharField(max_length=20)
    week9 = models.CharField(max_length=20)
    week10 = models.CharField(max_length=20)
    week11 = models.CharField(max_length=20)
    week12 = models.CharField(max_length=20)
    week13 = models.CharField(max_length=20)
    week14 = models.CharField(max_length=20)
    week15 = models.CharField(max_length=20)
    week16 = models.CharField(max_length=20)
    week17 = models.CharField(max_length=20)
    week18 = models.CharField(max_length=20)
