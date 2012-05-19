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

