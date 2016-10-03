from django.conf.urls import url
from packet import views

urlpatterns = [
    url(r'^drop/$', views.drop, name="drop"),
    url(r'^nearby/fetch/$', views.fetch, name="fetch"),
    url(r'^pick/$', views.pick, name="pick"),
    url(r'^redrop/$', views.redrop, name="redrop"),
]
