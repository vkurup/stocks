from django.db import models

class Transaction(models.Model):
    action = models.CharField(max_length=10)
    date = models.DateTimeField('transaction date')
    security = models.CharField(max_length=10)
    shares = models.DecimalField(decimal_places=2, max_digits=10)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    commission = models.DecimalField(decimal_places=2, max_digits=10)

    def __unicode__(self):
        return self.action + ' ' + str(self.shares) + ' ' + self.security

