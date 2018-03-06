from django.conf.urls import url
from . import views

app_name = 'lectures'

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^search/', views.search, name='search_course'),
]