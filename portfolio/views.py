from portfolio.models import Transaction
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView

class MainView(TemplateView):
    template_name = "portfolio.html"

class TransactionListView(ListView):
    model = Transaction

class TransactionDetailView(UpdateView):
    model = Transaction
    success_url = "/portfolio/txn"

class TransactionCreateView(CreateView):
    model = Transaction
    success_url = "../txn"

class TransactionDeleteView(DeleteView):
    model = Transaction
    success_url = "/portfolio/txn"

