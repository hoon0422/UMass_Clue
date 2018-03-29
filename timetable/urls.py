from django.urls import path
from . import views

app_name = 'timetable'
urlpatterns = [
    path('test/', views.TimetableView.as_view(), name='timetable_test'),
]
