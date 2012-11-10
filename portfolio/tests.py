"""
Tests for portfolio app
"""

import factory
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from models import Transaction, Account
import datetime


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

        edited_txn = Transaction.objects.get(pk=txn.pk)

        self.assertEquals(float(edited_txn.price), 21.32)

    def test_delete_transaction(self):
        TransactionFactory()
        txn = Transaction.objects.all()[0]
        txn.delete()
        txn = Transaction.objects.filter(pk=txn.pk)
        self.assertTrue(len(txn) == 0)


class AccountTest(TestCase):

    def setUp(self):
        self.a = Account()
        self.a.save()

    def test_create_account(self):
        self.assertTrue(self.a)

    def test_deposit(self):
        self.a.deposit(amount=1000.12, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['$CASH']['shares'], Decimal('1000.12'))

    def test_withdraw(self):
        self.a.withdraw(amount=10, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['$CASH']['shares'], Decimal('-10'))

    def test_buy_security(self):
        self.a.buy_security(security='AAPL',
                            shares=100,
                            price=29.27,
                            date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['AAPL']['shares'], 100)

    def test_buy_more_security(self):
        self.a.buy_security(security='AAPL', shares=100,
                            price=29.27, date=timezone.now())
        self.a.buy_security(security='AAPL', shares=50,
                            price=29.45, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['AAPL']['shares'], 150)

    def test_sell_security(self):
        self.a.deposit(amount=10000, date=timezone.now())
        self.a.buy_security(security='AAPL', shares=100,
                            price=29.27, date=timezone.now())
        self.a.sell_security(security='AAPL', shares=99,
                             price=29.27, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['AAPL']['shares'], 1)

    def test_dividend(self):
        self.a.deposit(amount=1000, date=timezone.now())
        self.a.buy_security(security='AAPL', shares=100,
                            price=10.00, date=timezone.now())
        self.a.dividend(security='AAPL', amount=10.00, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['$CASH']['shares'], 10.00)

    def test_receive_interest(self):
        self.a.deposit(amount=100, date=timezone.now())
        self.a.receive_interest(amount=5.89, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['$CASH']['shares'], Decimal('105.89'))

    def test_pay_interest(self):
        self.a.withdraw(amount=100, date=timezone.now())
        self.a.pay_interest(amount=5.89, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['$CASH']['shares'], Decimal('-105.89'))

    def test_buy_security_uses_cash(self):
        self.a.buy_security(security='AAPL', shares=10,
                            price=29.45, date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['$CASH']['shares'], Decimal('-294.50'))

    def test_buy_security_check_security_value(self):
        self.a.buy_security(security='AAPL', shares=10,
                            price=29.45, commission=10,
                            date=timezone.now())
        value = self.a.mktval(security='AAPL')
        self.assertEquals(value, 294.50)

    def test_buy_security_check_account_value(self):
        self.a.deposit(amount=10000, date=timezone.now())
        self.a.buy_security(security='AAPL', shares=10,
                            price=15.00, commission=20,
                            date=timezone.now())
        self.a.receive_interest(amount=10.00, date=timezone.now())
        value = self.a.mktval()
        cash = self.a.mktval(security='$CASH')
        self.assertEquals(value, 9990.00)
        self.assertEquals(cash, 9840.00)

    def test_buy_security_check_security_basis(self):
        self.a.buy_security(security='AAPL', shares=10,
                            price=29.45, commission=10,
                            date=timezone.now())
        basis = self.a.basis(security='AAPL')
        self.assertEquals(basis, 304.50)

    def test_buy_security_check_account_basis(self):
        self.a.deposit(amount=10000, date=timezone.now())
        self.a.buy_security(security='AAPL', shares=10,
                            price=15.00, commission=20,
                            date=timezone.now())
        self.a.receive_interest(amount=10.00, date=timezone.now())
        basis = self.a.basis()
        cash = self.a.basis(security='$CASH')
        self.assertEquals(basis, 10000.00)
        self.assertEquals(cash, 9830.00)

    def test_deposit_sets_cash(self):
        self.a.deposit(amount=123.45, date=timezone.now())
        cash = self.a.cash['shares']
        self.assertEquals(cash, Decimal('123.45'))

    def test_account_transactions_are_separate(self):
        self.a.deposit(amount=5, date=timezone.now())
        b = Account()
        b.save()
        b.deposit(amount=10, date=timezone.now())
        self.assertEquals(self.a.cash['shares'], 5)
        self.assertEquals(b.cash['shares'], 10)

    def test_cost_basis_is_correct(self):
        self.a.buy_security(security='AAPL', shares=100,
                            price=20.00, date=timezone.now())
        positions = self.a.positions()
        cost_basis = positions['AAPL']['basis']
        self.assertEquals(cost_basis, 2000)

    def test_cost_basis_includes_commission(self):
        self.a.buy_security(security='AAPL', shares=100,
                            price=20.00, commission=7.00,
                            date=timezone.now())
        positions = self.a.positions()
        cost_basis = positions['AAPL']['basis']
        self.assertEquals(cost_basis, 2007)

    def test_cost_basis_multiple_buys(self):
        self.a.buy_security(security='AAPL', shares=100,
                            price=8.00, commission=3.00,
                            date=timezone.now())
        self.a.buy_security(security='AAPL', shares=200,
                            price=6.00, commission=4.00,
                            date=timezone.now())
        positions = self.a.positions()
        cost_basis = positions['AAPL']['basis']
        self.assertEquals(cost_basis, 2007)

    def test_cost_basis_after_sell(self):
        self.a.buy_security(security='AAPL', shares=100,
                            price=20.00, commission=0,
                            date=timezone.now())
        self.a.sell_security(security='AAPL', shares=50,
                             price=30, date=timezone.now())
        positions = self.a.positions()
        cost_basis = positions['AAPL']['basis']
        self.assertEquals(cost_basis, 1000)

    def test_market_value_doesnt_include_commission(self):
        self.a.deposit(amount=10000, date=timezone.now())
        self.a.buy_security(security='AAPL', shares=100,
                            commission=7.00,
                            price=20.00, date=timezone.now())
        positions = self.a.positions()
        market_value = positions['AAPL']['mktval']
        self.assertEquals(market_value, 2000)

    def test_market_value_for_2_buys(self):
        june = datetime.date(2011, 6, 1)
        july = datetime.date(2011, 7, 1)
        self.a.deposit(amount=10000, date=timezone.now())
        self.a.buy_security(security='AAPL', shares=100,
                            commission=7.00,
                            price=20.00, date=june)
        self.a.buy_security(security='AAPL', shares=10,
                            commission=5.00,
                            price=23.00, date=july)
        positions = self.a.positions()
        market_value = positions['AAPL']['mktval']
        self.assertEquals(market_value, 2530)

    def test_gain_is_correct(self):
        self.a.deposit(amount=10000, date=timezone.now())
        self.a.buy_security(security='AAPL', shares=100,
                            commission=7.00,
                            price=20.00, date=timezone.now())
        positions = self.a.positions()
        gain = positions['AAPL']['gain']
        self.assertEquals(gain, -7)

    def test_positions_includes_only_past_dates(self):
        june = datetime.date(2011, 6, 1)
        july = datetime.date(2011, 7, 1)
        august = datetime.date(2011, 8, 1)
        self.a.deposit(amount=10000, date=june)
        self.a.buy_security(security='AAPL', shares=100,
                            price=20, date=june)
        self.a.buy_security(security='AAPL', shares=200,
                            price=20, date=august)
        positions = self.a.positions(date=july)
        aapl = positions['AAPL']['shares']
        self.assertEquals(aapl, 100)

    def test_interest_doesnt_affect_basis(self):
        self.a.deposit(amount=100, date=timezone.now())
        self.a.receive_interest(amount=5.89, date=timezone.now())
        basis = self.a.basis()
        self.assertEquals(basis, 100)

    def test_stock_split_adjusts_shares(self):
        self.a.buy_security(security='AAPL', shares=100,
                            price=20.00, date=timezone.now())
        self.a.stock_split(security='AAPL', split_ratio=2.0,
                           date=timezone.now())
        positions = self.a.positions()
        self.assertEquals(positions['AAPL']['shares'], 200)

    def test_no_error_if_no_basis(self):
        cash = self.a.cash['shares']
        self.assertEquals(cash, 0)
