from django.conf.urls import url
from . import views

app_name = 'lectures'

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^search/(?P<lecture>.+)/$', views.search_lecture, name='search_lecture'),
    url(r'^search/(?P<professor>.+)/$', views.search_professor, name='search_professor'),
    url(r'^search/(?P<building>.+)/$', views.search_building, name='search_building'),
]