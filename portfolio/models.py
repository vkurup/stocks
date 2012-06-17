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
            else:
                positions[t.security]['basis'] += t.shares * t.price + t.commission
            positions[t.security]['shares'] += t.shares
            positions[t.security]['price'] = t.price
            basis = positions[t.security]['basis']
            mktval = positions[t.security]['shares'] * t.price
            positions[t.security]['mktval'] = mktval
            positions[t.security]['gain'] = mktval - basis
            dividends = positions[t.security]['dividends']
            positions[t.security]['total_return'] = ((mktval + dividends)/basis - 1) * 100

            if t.action == 'DIV':
                positions[t.dividend_from]['dividends'] += t.shares * t.price
        return positions

    def value(self, security=None):
        positions = self.positions()
        if security:
            return positions[security]['shares'] * positions[security]['price']
        else:
            value = sum(positions[p]['shares'] * positions[p]['price'] for p in positions)
            return value
    
    def total_return(self, security=None):
        value = self.value(security)
        positions = self.positions()
        return value + positions[security]['dividends']

    @property
    def cash(self):
        positions = self.positions()
        return float(positions['$CASH']['shares'])




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

