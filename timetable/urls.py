from django.urls import path
from . import views

app_name = 'timetable'
urlpatterns = [
    path('test/', views.TimetableView.as_view(), name='timetable_test_default'),
    path('test/<int:id>', views.TimetableView.as_view(), name='timetable_test'),
    path('test/<int:current_timetable_id>/ajax/add', views.add_new_timetable, name='timetable_ajax_add'),
    path('test/<int:current_timetable_id>/ajax/remove', views.remove_timetable, name='timetable_ajax_remove'),
]
