from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

app_name = 'coffee'
urlpatterns = [
    url(r'^$', RedirectView.as_view(url='order/')),
    url(r'^list/$', views.list_coffee, name='list_coffee'),
    url(r'^order/$', views.list_order, name='list_order'),
    url(r'^content_order/(?P<order_id>[0-9]+)/$', views.list_content_order, name='list_content_order'),
    url(r'^content_order/del/(?P<content_id>\d+)/$', views.remove_coffee_of_your_content_order, name='remove_coffee_of_your_content_order'),
    # url(r'^$', views.IndexView.as_view(), name='index'),
    # url(r'^manage/$', views.manage_coffee, name='manage_coffee'),
    # url(r'^manage/sync/$', views.sync_coffee, name='sync_coffee'),
    # url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    # url(r'^choice/sync/(?P<question_id>[0-9]+)/$', views.sync_choice, name='sync_choice'),
    # url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    # url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
]
