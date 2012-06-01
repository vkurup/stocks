from django.conf.urls import patterns
from portfolio.views import *

urlpatterns = patterns(
    '',
    (r'^$', AccountListView.as_view()),
    (r'^account/(?P<pk>\d+)/$', AccountDetailView.as_view()),
    (r'^account/(?P<pk>\d+)/edit$', AccountEditView.as_view()),
    (r'^account/(?P<account_id>\d+)/deposit$', 'portfolio.views.deposit'),
    (r'^account/create$', AccountCreateView.as_view()),
    (r'^txn/$', TransactionListView.as_view()),
    (r'^txn/(?P<pk>\d+)/$', TransactionDetailView.as_view()),
    (r'^txn/create$', TransactionCreateView.as_view()),
    (r'^txn/(?P<pk>\d+)/delete$', TransactionDeleteView.as_view()),
)
