from portfolio.models import Transaction
from django.views.generic import ListView, DetailView, TemplateView, CreateView

class MainView(TemplateView):
    template_name = "portfolio.html"

class TransactionListView(ListView):
    model = Transaction

class TransactionDetailView(DetailView):
    model = Transaction

class TransactionCreateView(CreateView):
    model = Transaction
    success_url = "../txn"
