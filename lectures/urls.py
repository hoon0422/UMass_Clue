from django.urls import path
from . import views

app_name = 'lectures'

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('search/', views.SearchView.as_view(), name='search_course'),
    path('detail/<pk>/', views.DetailView.as_view(), name='detail')
]