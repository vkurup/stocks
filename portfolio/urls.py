from django.conf.urls import patterns, url, include
from django.views.generic import ListView, DetailView
from portfolio.models import Transaction

urlpatterns = patterns(
    '',
    (r'^$', ListView.as_view(
            model=Transaction)),
    (r'^(?P<pk>\d+)/$', DetailView.as_view(
            model=Transaction)),
)
