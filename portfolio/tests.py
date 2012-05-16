"""
Tests for portfolio app
"""

import factory
from django.test import TestCase
from django.utils import timezone
from portfolio.models import Transaction

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

