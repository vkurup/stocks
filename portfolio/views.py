from portfolio.models import Transaction, Account
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

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

class AccountDetailView(DetailView):
    model = Account

class AccountEditView(UpdateView):
    model = Account
    success_url = "/portfolio/account"

class AccountCreateView(CreateView):
    model = Account
    success_url = "/portfolio/account"

class AccountDeleteView(DeleteView):
    model = Account
    success_url = "/portfolio/account"


# Functions
def deposit(request, account_id):
    if request.method == 'GET':
        return render(request, 'portfolio/deposit.html')
    else:
        a = get_object_or_404(Account, pk=account_id)
        amount = request.POST['amount']
        a.deposit(amount, timezone.now())
        return redirect('/portfolio/account/' + account_id)
