from django.shortcuts import render
from django.views import generic
from .models import *
from lectures.forms import *


class IndexView(generic.TemplateView):
    template_name = "lectures/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(kwargs=kwargs)
        context["search_form"] = SearchForm(self.request.POST, self.request.FILES)
        return context


class SearchView(IndexView):
    template_name = "lectures/search.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(kwargs=kwargs)
        option = self.get_search_option()
        if option == "Course":
            courses = SearchView.search_course(self.get_search_key())
        elif option == "Professor":
            courses = SearchView.search_professor(self.get_search_key())
        elif option == "Room":
            courses = SearchView.search_room(self.get_search_key())
        else:
            courses = []
        context["courses"] = courses
        return context

    def get_search_option(self):
        return self.request.GET["search_option"]

    def get_search_key(self):
        return self.request.GET["search_key"]

    @staticmethod
    def search_course(course_key):
        return Course.objects.filter(title__contains=course_key)

    @staticmethod
    def search_professor(professor_key):
        return Course.objects.filter(session__professors__name__contains=professor_key)

    @staticmethod
    def search_room(building_key):
        return Course.objects.filter(session__room__name__contains=building_key)
