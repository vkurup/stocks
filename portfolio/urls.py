from django.conf.urls import patterns
from portfolio.views import *

urlpatterns = patterns(
    '',
    (r'^$', MainView.as_view()),
    (r'^account/$', AccountListView.as_view()),
    (r'^account/(?P<pk>\d+)/$', AccountDetailView.as_view()),
    (r'^account/create$', AccountCreateView.as_view()),
    (r'^txn/$', TransactionListView.as_view()),
    (r'^txn/(?P<pk>\d+)/$', TransactionDetailView.as_view()),
    (r'^txn/create$', TransactionCreateView.as_view()),
    (r'^txn/(?P<pk>\d+)/delete$', TransactionDeleteView.as_view()),
)
