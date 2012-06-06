"""
Tests for portfolio app
"""

import factory
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from models import Transaction, Account

class TransactionFactory(factory.Factory):
    FACTORY_FOR = Transaction

    account_id = 1
    action = 'BUY'
    date = timezone.now()
    security = 'AAPL'
    shares = 100
    price = 29.27
    commission = 7.00


class TransactionTest(TestCase):
    def test_create_transaction(self):
        before = len(Transaction.objects.all())
        TransactionFactory()
        after = len(Transaction.objects.all())
        self.assertEquals(after - before, 1)

    def test_edit_transaction(self):
        TransactionFactory()
        txn = Transaction.objects.all()[0]

        txn.price = 21.32
        txn.save()

        edited_txn = Transaction.objects.get(pk = txn.pk)

        self.assertEquals(float(edited_txn.price), 21.32)

    def test_delete_transaction(self):
        TransactionFactory()
        txn = Transaction.objects.all()[0]
        txn.delete()
        txn = Transaction.objects.filter(pk = txn.pk)
        self.assertTrue(len(txn) == 0)

class AccountTest(TestCase):

    def setUp(self):
        self.a = Account()
        self.a.save()

    def test_create_account(self):
        self.assertTrue(self.a)

    def test_buy_security(self):
        self.a.buy_security(security='AAPL', shares=100, price=29.27, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['AAPL']['shares'], 100)

    def test_buy_more_security(self):
        self.a.buy_security(security='AAPL', shares=100, price=29.27, date=timezone.now())
        self.a.buy_security(security='AAPL', shares=50, price=29.45, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['AAPL']['shares'], 150)

    def test_sell_security(self):
        self.a.sell_security(security='AAPL', shares=100, price=29.27, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['AAPL']['shares'], -100)

    def test_dividend(self):
        self.a.dividend(security='AAPL', amount=10.00, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['$CASH']['shares'], 10.00)

    def test_deposit(self):
        self.a.deposit(amount=1000.12, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['$CASH']['shares'], Decimal('1000.12'))

    def test_withdraw(self):
        self.a.withdraw(amount=12.34, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['$CASH']['shares'], Decimal('-12.34'))

    def test_receive_interest(self):
        self.a.receive_interest(amount=5.89, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['$CASH']['shares'], Decimal('5.89'))

    def test_pay_interest(self):
        self.a.pay_interest(amount=33.31, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['$CASH']['shares'], Decimal('-33.31'))

    def test_buy_security_uses_cash(self):
        self.a.deposit(amount=1000.12, date=timezone.now())
        self.a.buy_security(security='AAPL', shares=10, price=29.45, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['$CASH']['shares'], Decimal('1000.12') - Decimal('294.50'))

    def test_buy_security_check_security_value(self):
        self.a.buy_security(security='AAPL', shares=10, 
                            price=29.45, date=timezone.now())
        value = self.a.value(security='AAPL')
        self.assertEquals(value, 294.50)

    def test_buy_security_check_account_value(self):
        self.a.deposit(amount=1000.00, date=timezone.now())
        self.a.buy_security(security='AAPL', shares=10,
                            price=15.00, date=timezone.now())
        self.a.receive_interest(amount=10.00, date=timezone.now())
        value = self.a.value()
        cash = self.a.value(security='$CASH')
        self.assertEquals(value, 1010.00)
        self.assertEquals(cash, 860.00)

    def test_security_plus_dividend_correct_return(self):
        self.a.buy_security(security='AAPL', shares=10,
                            price=15.00, date=timezone.now())
        self.a.dividend(security='AAPL', amount=10.00, date=timezone.now())
        tr = self.a.total_return(security='AAPL')
        self.assertEquals(tr, 160.00)

    def test_deposit_sets_cash(self):
        self.a.deposit(amount=123.45, date=timezone.now())
        cash = self.a.cash
        self.assertEquals(cash, 123.45)

    def test_account_transactions_are_separate(self):
        self.a.deposit(amount=5, date=timezone.now())
        b = Account()
        b.save()
        b.deposit(amount=10, date=timezone.now())
        self.assertEquals(self.a.cash, 5)
        self.assertEquals(b.cash, 10)
