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

class Account(models.Model):

    def buy_security(self, action="BUY", security=None, shares=None, date=None, price=None, commission=0):
        t = Transaction()
        t.action = action
        t.security = security
        t.shares = shares
        t.date = date
        t.price = price
        t.commission = commission
        t.save()

        # other side of double-entry
        #FIXME for CASH
        if security != '$CASH':
            cost = t.shares * t.price + t.commission
            self.sell_security(security = '$CASH', shares = cost, date=date, price=1.00)

    def sell_security(self, security=None, shares=None, date=None, price=None, commission=0):
        self.buy_security(action="SELL", security=security, shares=-shares, date=date, price=price, commission=commission)

    def dividend(self, security=None, amount=0.00, date=None):
        # fixme, this throws away security. Not sure where it should go
        self.buy_security(action="DIV", security='$CASH', shares=amount, date=date, price=1.00)

    def deposit(self, amount=0, date=None):
        self.buy_security(action="DEPOSIT", security='$CASH', shares=amount, date=date, price=1.00)

    def withdraw(self, amount=0, date=None):
        self.deposit(amount = -amount, date=date)

    def receive_interest(self, amount=0, date=None):
        self.buy_security(action="INT", security='$CASH', shares=amount, date=date, price=1.00)

    def pay_interest(self, amount=0, date=None):
        self.receive_interest(-amount, date)

    def positions(self):
        txns = Transaction.objects.all()
        positions = {}
        for t in txns:
            if t.security in positions:
                positions[t.security]['shares'] += t.shares
                positions[t.security]['price'] = t.price
            else:
                positions[t.security] = {'shares': t.shares,
                                         'price': t.price}
        return positions

    def value(self, security=None):
        pos = self.positions()
        if security:
            return pos[security]['shares'] * pos[security]['price']
        else:
            value = 0
            for p in pos:
                value += pos[p]['shares'] * pos[p]['price']
            return value

