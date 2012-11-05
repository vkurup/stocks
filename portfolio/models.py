from django.db import models
from decimal import Decimal
from django.utils import timezone

class Account(models.Model):
    name = models.CharField(max_length=50)

    def buy_security(self, action="BUY", security=None, shares=None, date=None, price=None, dividend_from='', commission=0):
        t = Transaction()
        t.account = self
        t.action = action
        t.security = security
        t.shares = Decimal(shares)
        t.date = date
        t.price = Decimal(price)
        t.dividend_from = dividend_from
        t.commission = Decimal(commission)
        t.save()

        # update Price table
        p = Price()
        p.date = date
        p.security = security
        p.price = price
        p.save()

        # other side of double-entry
        #FIXME for CASH
        if security != '$CASH':
            cost = t.shares * t.price + t.commission
            self.sell_security(security = '$CASH', shares = cost, date=date, price=1.00)

    def sell_security(self, security=None, shares=None, date=None, price=None, commission=0):
        self.buy_security(action="SELL", security=security, shares=-shares, date=date, price=price, commission=commission)

    def dividend(self, security=None, amount=0.00, date=None):
        self.buy_security(action="DIV", security='$CASH', dividend_from=security, shares=amount, date=date, price=1.00)

    def deposit(self, amount=0, date=None):
        self.buy_security(action="DEPOSIT", security='$CASH', shares=amount, date=date, price=1.00)

    def withdraw(self, amount=0, date=None):
        self.deposit(amount = -amount, date=date)

    def receive_interest(self, amount=0, date=None):
        self.buy_security(action="INT", security='$CASH', shares=amount, date=date, price=1.00)

    def pay_interest(self, amount=0, date=None):
        self.receive_interest(-amount, date)

    def new_position(self):
        return dict(shares=0, price=1, basis=0,
                    mktval=0, gain=0, dividends=0,
                    total_return=0)

    def positions(self, date=None):
        """Return a dictionary of all of the positions in this account.

        If date is provided, then only include transactions up to (and
        including) that date."""
        if not date:
            date = timezone.now()
        positions = {'$CASH': self.new_position()}
        txns = Transaction.objects.filter(account=self, date__lte=date).order_by('date','id')
        for t in txns:
            if t.security not in positions:
                positions[t.security] = self.new_position()
            if t.dividend_from and t.dividend_from not in positions:
                positions[t.dividend_from] = self.new_position()
            if t.action == 'SELL':
                current_shares = positions[t.security]['shares']
                if current_shares:
                    old_basis_ps = positions[t.security]['basis'] / positions[t.security]['shares']
                else:
                    old_basis_ps = t.price
                positions[t.security]['basis'] += old_basis_ps * t.shares
            elif t.action == 'INT':
                pass
            else:
                positions[t.security]['basis'] += t.shares * t.price + t.commission
            positions[t.security]['shares'] += t.shares
            basis = positions[t.security]['basis']
            dividends = positions[t.security]['dividends']
            latest_price = Price.objects.filter(security=t.security, date__lte=date).latest('date').price
            positions[t.security]['price'] = latest_price
            mktval = positions[t.security]['shares'] * latest_price
            positions[t.security]['mktval'] = mktval
            positions[t.security]['gain'] = mktval - basis
            if basis:
                positions[t.security]['total_return'] = ((mktval + dividends)/basis - 1) * 100
            else:
                positions[t.security]['total_return'] = 0

            if t.action == 'DIV':
                positions[t.dividend_from]['dividends'] += t.shares * t.price
        return positions

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
        return float(positions['$CASH']['shares'])


class Price(models.Model):
    date = models.DateField('transaction date')
    security = models.CharField(max_length=10)
    price = models.DecimalField(decimal_places=2, max_digits=10)

class Transaction(models.Model):
    account = models.ForeignKey(Account)
    action = models.CharField(max_length=10)
    date = models.DateField('transaction date')
    security = models.CharField(max_length=10)
    shares = models.DecimalField(decimal_places=2, max_digits=10)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    commission = models.DecimalField(decimal_places=2, max_digits=10)
    dividend_from = models.CharField(max_length=10, blank=True)

    def __unicode__(self):
        return self.action + ' ' + str(self.shares) + ' ' + self.security
