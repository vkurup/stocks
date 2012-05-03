from django.conf.urls import patterns, url

urlpatterns = patterns(
    'portfolio.views',
    url(r'^$', 'index'),
    url(r'^(?P<txn_id>\d+)/$', 'detail'),
)
