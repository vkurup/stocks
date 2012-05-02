"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils import timezone
from portfolio.models import Transaction

class TransactionTest(TestCase):
    def test_create_transaction(self):
        txn = Transaction()
        txn.action = "BUY"
        txn.date = timezone.now()

        txn.save()

        all_txns = Transaction.objects.all()
        self.assertEquals(len(all_txns), 1)
        self.assertEquals(all_txns[0], txn)

        self.assertEquals(all_txns[0].action, "BUY")
        self.assertEquals(all_txns[0].date, txn.date)

