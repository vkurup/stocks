from portfolio.models import Transaction
from django.shortcuts import render, get_object_or_404

def index(request):
    transaction_list = Transaction.objects.all().order_by('-date')
    return render(request, 'portfolio/index.html', {'transaction_list': transaction_list})

def detail(request, txn_id):
    t = get_object_or_404(Transaction, pk=txn_id)
    return render(request, 'portfolio/detail.html', {'transaction': t})
