from django.db import models

class Account(models.Model):
    name = models.CharField(max_length=100)
    taxable = models.BooleanField()

    def __unicode__(self):
        return self.name

class Security(models.Model):
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100) # stock, MF, ETF
    exchange = models.CharField(max_length=100)

    def __unicode__(self):
        return self.symbol

class ClosingPrice(models.Model):
    security = models.ForeignKey(Security)
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=10,decimal_places=2)

class Transaction(models.Model):
    date = models.DateTimeField()
    action = models.CharField(max_length=100) # BUY, SELL, DIV, INT, RD, RI, SS
    security = models.ForeignKey(Security)
    shares = models.DecimalField(max_digits=10,decimal_places=2)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    commission = models.DecimalField(max_digits=10,decimal_places=2)
    account = models.ForeignKey(Account)

    def __unicode__(self):
        return self.action + " " + str(self.shares) + " " + str(self.security)

    
