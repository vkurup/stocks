from django.conf.urls import patterns, url, include
from django.views.generic import ListView, DetailView, TemplateView
from portfolio.models import Transaction

urlpatterns = patterns(
    '',
    (r'^$', TemplateView.as_view(
            template_name="portfolio.html")),
    (r'^txn/$', ListView.as_view(
            model=Transaction,
            template_name="transaction_list.html")),
    (r'^txn/(?P<pk>\d+)/$', DetailView.as_view(
            model=Transaction,
            template_name="transaction_detail.html")),
)
