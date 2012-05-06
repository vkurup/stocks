from django.conf.urls import patterns
from portfolio.views import MainView, TransactionListView, TransactionDetailView, TransactionCreateView, TransactionDeleteView

urlpatterns = patterns(
    '',
    (r'^$', MainView.as_view()),
    (r'^txn/$', TransactionListView.as_view()),
    (r'^txn/(?P<pk>\d+)/$', TransactionDetailView.as_view()),
    (r'^txn/create$', TransactionCreateView.as_view()),
    (r'^txn/(?P<pk>\d+)/delete$', TransactionDeleteView.as_view()),
)
