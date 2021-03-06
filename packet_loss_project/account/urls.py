from django.conf.urls import url
from account import views

urlpatterns = [
    url(r'^login/$', views.user_login, name="login"),
    url(r'^register/$', views.register, name="register"),
    url(r'^logout/$', views.user_logout, name="logout"),
    url(r'^password/$', views.change_password, name="password"),
    url(r'^details/$', views.user_details, name="details")
]
