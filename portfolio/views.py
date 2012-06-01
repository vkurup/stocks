from portfolio.models import Transaction, Account
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

class TransactionListView(ListView):
    model = Transaction

class TransactionDetailView(UpdateView):
    model = Transaction
    success_url = "/portfolio/txn"

class TransactionCreateView(CreateView):
    model = Transaction
    success_url = "/portfolio/txn"

class TransactionDeleteView(DeleteView):
    model = Transaction
    success_url = "/portfolio/txn"


class AccountListView(ListView):
    model = Account

class AccountDetailView(UpdateView):
    model = Account
    success_url = "/portfolio/account"

class AccountCreateView(CreateView):
    model = Account
    success_url = "/portfolio/account"

class AccountDeleteView(DeleteView):
    model = Account
    success_url = "/portfolio/account"
