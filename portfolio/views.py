from portfolio.models import Transaction, Account
from portfolio.forms import BuyForm, DepositForm, InterestForm
from django.shortcuts import render, redirect, get_object_or_404
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
    success_url = "/portfolio"

class AccountCreateView(CreateView):
    model = Account
    success_url = "/portfolio"

class AccountDeleteView(DeleteView):
    model = Account
    success_url = "/portfolio"


# Functions
def deposit(request, account_id):
    a = get_object_or_404(Account, pk=account_id)
    if request.method == 'GET':
        form = DepositForm()
    else:
        form = DepositForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            amount = form.cleaned_data['amount']
            a.deposit(amount=amount, date=date)
            return redirect('/portfolio/account/' + account_id)
    return render(request, 'portfolio/deposit.html', {'form': form})

def buy(request, account_id):
    a = get_object_or_404(Account, pk=account_id)
    if request.method == 'GET':
        form = BuyForm()
    else:
        form = BuyForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            security = form.cleaned_data['security']
            shares = form.cleaned_data['shares']
            price = form.cleaned_data['price']
            commission = form.cleaned_data['commission']
            a.buy_security(security=security, shares=shares, date=date,
                           price=price, commission=commission)
            return redirect('/portfolio/account/' + account_id)
    return render(request, 'portfolio/buy.html', {'form': form})

def interest(request, account_id):
    a = get_object_or_404(Account, pk=account_id)
    if request.method == 'GET':
        form = InterestForm()
    else:
        form = InterestForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            amount = form.cleaned_data['amount']
            a.receive_interest(amount=amount, date=date)
            return redirect('/portfolio/account/' + account_id)
    return render(request, 'portfolio/interest.html', {'form': form})
