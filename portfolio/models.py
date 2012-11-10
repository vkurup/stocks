from django.db import models
from decimal import Decimal
from django.utils import timezone


class Account(models.Model):
    name = models.CharField(max_length=50)

    def buy_security(self, security=None, shares=None, date=None,
                     price=None, commission=0):
        t = Transaction()
        t.account = self
        t.action = 'BUY'
        t.security = security
        t.shares = Decimal(shares)
        t.date = date
        t.price = Decimal(price)
        t.commission = Decimal(commission)
        t.save()

        Price.objects.create(date=date, security=security,
                             price=price)

    def sell_security(self, security=None, shares=None, date=None,
                      price=None, commission=0, sec_fee=0):
        t = Transaction()
        t.account = self
        t.action = 'SELL'
        t.security = security
        t.shares = Decimal(shares)
        t.date = date
        t.price = Decimal(price)
        t.commission = Decimal(commission)
        t.sec_fee = Decimal(sec_fee)
        t.save()

        Price.objects.create(date=date, security=security,
                             price=price)

    def dividend(self, security=None, amount=0.00, date=None):
        t = Transaction()
        t.account = self
        t.action = 'DIV'
        t.security = security
        t.date = date
        t.cash_amount = Decimal(amount)
        t.save()

    def deposit(self, amount=0, date=None):
        t = Transaction()
        t.account = self
        t.action = 'DEP'
        t.cash_amount = Decimal(amount)
        t.date = date
        t.save()

    def withdraw(self, amount=0, date=None):
        t = Transaction()
        t.account = self
        t.action = 'WITH'
        t.cash_amount = Decimal(-amount)
        t.date = date
        t.save()

    def receive_interest(self, amount=0, date=None):
        t = Transaction()
        t.account = self
        t.action = 'INT'
        t.cash_amount = Decimal(amount)
        t.date = date
        t.save()

    def pay_interest(self, amount=0, date=None):
        t = Transaction()
        t.account = self
        t.action = 'MARGIN'
        t.cash_amount = Decimal(-amount)
        t.date = date
        t.save()

    def stock_split(self, security=None, split_ratio=0, date=None):
        t = Transaction()
        t.account = self
        t.action = 'SS'
        t.security = security
        t.split_ratio = split_ratio
        t.date = date
        t.save()

    def new_position(self):
        return dict(shares=0, price=1, basis=0,
                    mktval=0, gain=0, dividends=0,
                    total_return=0)

    def update_market_value(self, positions, date):
        for security in positions:
            p = positions[security]
            if security == '$CASH':
                price = 1.00
            else:
                price = Price.objects.filter(
                    security=security, date__lte=date).latest('date').price
            mktval = p['shares'] * Decimal(price)
            gain = mktval - p['basis']
            if p['basis']:
                tr = ((mktval + p['dividends']) / p['basis'] - 1) * 100
            else:
                tr = 0
            positions[security]['mktval'] = mktval
            positions[security]['gain'] = gain
            positions[security]['total_return'] = tr
            positions[security]['price'] = price
        return positions

    def positions(self, date=None):
        """Return a dictionary of all of the positions in this account.

        If date is provided, then only include transactions up to (and
        including) that date."""
        if not date:
            date = timezone.now()
        positions = {'$CASH': self.new_position()}
        txns = Transaction.objects.filter(
            account=self, date__lte=date).order_by('date', 'id')
        for t in txns:
            if t.security and t.security not in positions:
                positions[t.security] = self.new_position()

            # switch based on transaction action
            if t.action in ('DEP', 'WITH'):
                positions['$CASH']['basis'] += t.cash_amount
                positions['$CASH']['shares'] += t.cash_amount
            elif t.action in ('INT', 'MARGIN'):
                positions['$CASH']['shares'] += t.cash_amount
            elif t.action == 'DIV':
                positions['$CASH']['basis'] += t.cash_amount
                positions['$CASH']['shares'] += t.cash_amount
                positions[t.security]['dividends'] += t.cash_amount
            elif t.action == 'SS':
                positions[t.security]['shares'] *= t.split_ratio
            elif t.action == 'BUY':
                positions[t.security]['basis'] += (
                    t.shares * t.price + t.commission)
                positions[t.security]['shares'] += t.shares
                cost = t.shares * t.price + t.commission
                positions['$CASH']['basis'] -= cost
                positions['$CASH']['shares'] -= cost
            elif t.action == 'SELL':
                current_shares = positions[t.security]['shares']
                if current_shares:
                    old_basis_ps = (positions[t.security]['basis'] /
                                    positions[t.security]['shares'])
                else:
                    old_basis_ps = t.price
                positions[t.security]['basis'] -= old_basis_ps * t.shares
                positions[t.security]['shares'] -= t.shares
        return self.update_market_value(positions, date)

    def value(self, security=None):
        positions = self.positions()
        if security:
            return positions[security]['mktval']
        return sum(positions[p]['mktval'] for p in positions)

    def basis(self, security=None):
        positions = self.positions()
        if security:
            return positions[security]['basis']
        return sum(positions[p]['basis'] for p in positions)

    def gain(self, security=None):
        positions = self.positions()
        if security:
            return positions[security]['gain']
        return sum(positions[p]['gain'] for p in positions)

    def dividends(self, security=None):
        positions = self.positions()
        if security:
            return positions[security]['dividends']
        return sum(positions[p]['dividends'] for p in positions)

    def total_return(self, security=None):
        positions = self.positions()
        if security:
            return positions[security]['total_return']
        if self.basis():
            return ((self.value() + self.dividends()) / self.basis() - 1) * 100

    @property
    def cash(self):
        positions = self.positions()
        return positions['$CASH']


class Price(models.Model):
    date = models.DateField('transaction date')
    security = models.CharField(max_length=10)
    price = models.DecimalField(decimal_places=2, max_digits=10)


class Transaction(models.Model):
    account = models.ForeignKey(Account)
    action = models.CharField(max_length=10)
    date = models.DateField('transaction date')
    security = models.CharField(max_length=10, blank=True)
    shares = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    commission = models.DecimalField(decimal_places=2, max_digits=10,
                                     null=True)
    cash_amount = models.DecimalField(decimal_places=2, max_digits=10,
                                      null=True)
    sec_fee = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    split_ratio = models.DecimalField(decimal_places=2, max_digits=5,
                                      null=True)

    def __unicode__(self):
        return self.action + ' ' + str(self.shares) + ' ' + self.security
