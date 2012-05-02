from django.db import models

class Transaction(models.Model):
    action = models.CharField(max_length=10)
    date = models.DateTimeField('transaction date')
