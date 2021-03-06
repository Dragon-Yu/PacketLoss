from django.conf.urls import url
from packet import views

urlpatterns = [
    url(r'^drop/$', views.drop, name="drop"),
    url(r'^nearby/info/$', views.get_nearby_packets, name="get_nearby_packets"),
    url(r'^pick/$', views.pick, name="pick"),
    url(r'^redrop/$', views.redrop, name="redrop"),
    url(r'^details/$', views.get_packet_details, name="get_packet_details"),
    url(r'^list_owning_packets/$', views.get_owning_packets, name="get_owning_packets"),
    url(r'^list_owned_packets/$', views.get_owned_packets, name="get_owned_packets"),
    url(r'^ignore/$', views.ignore, name="ignore"),
]
