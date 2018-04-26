""" Views for the app

This module has views for "lectures" app.

"""

from django.views import generic
from .models import *
from lectures.forms import *
from timetable.models import Timetable
from django.http import JsonResponse
from django.urls import reverse
import time


class IndexView(generic.TemplateView):
    template_name = "lectures/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(kwargs=kwargs)

        # form for search
        context["search_form"] = SearchForm(self.request.GET, self.request.FILES)

        # form for detailed search
        context["detailed_search_form"] = DetailedSearchForm(self.request.GET, self.request.FILES)
        return context


class SearchView(generic.ListView):
    template_name = "lectures/search.html"
    context_object_name = "sections"  # search results
    paginate_by = 10

    def get_queryset(self):
        sections = Section.objects.filter(course__title__icontains=self.request.GET["search_key"])
        sorted(sections, key=lambda section: section.course.title.find(self.request.GET["search_key"]))
        # TODO: Bug - sorting with relevance works, but sorting with alphabetic order after relevance required

        return sections.order_by("-course__year_and_semester", "course__category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(kwargs=kwargs)

        # form for search
        context["search_form"] = SearchForm(self.request.GET, self.request.FILES)

        # the search key that user wrote for the search.
        context["search_key"] = self.request.GET["search_key"]
        return context


class DetailSearchView(SearchView):
    def get_queryset(self):
        if self.is_all_keys_empty():
            return []

        keymap = self.get_keymap()
        options = {}

        if keymap["course_title"] is not '':
            options["course__title__icontains"] = keymap["course_title"]

        if keymap['course_number'] is not '':
            options["course__number__icontains"] = keymap["course_title"]

        if keymap['class_number'] is not '':
            options["class__number__icontains"] = keymap["class_number"]

        if keymap['professor'] is not '':
            options["professors__name__icontains"] = keymap["class_number"]

        if keymap['year_and_semester'] is not '':
            options["course__year_and_semester__year"] = keymap["year_and_semester"]

        if keymap['time'] is not '':
            options["times__day__exact"] = keymap['time'][0]
            options["times__start_time__lte"] = keymap['time']
            # TODO: make time string to time field and use it on search.

    def get_context_data(self, **kwargs):
        # TODO: return search result.
        pass

    def get_keymap(self):
        """
        Return a map between search option and its value.
        :return: a map between search option and its value.
        """
        keymap = {
            'course_title': self.request.GET['course_title'],
            'course_number': self.request.GET['course_number'],
            'class_number': self.request.GET['class_number'],
            'professor': self.request.GET['professor'],
            'year_and_semester': self.request.GET['year_and_semester'],
            'time': self.request.GET['time']
        }

        if keymap['course_number'] == 'null':
            keymap['course_number'] = ''

        if keymap['year_and_semester'] == 'null':
            keymap['year_and_semester'] = ''

        if keymap['time'][0] == 'null':
            keymap['time'] = ''

        return keymap

    def is_all_keys_empty(self):
        """
        Check if all options are empty.
        :return: true if all options are empty, otherwise false.
        """
        return self.request.GET['course_title'] == '' and \
            self.request.GET['course_number'] == 'null' and \
            self.request.GET['class_number'] == '' and \
            self.request.GET['professor'] == '' and \
            self.request.GET['year_and_semester'] == '' and \
            self.request.GET['time'][0] == 'null'


class DetailView(generic.DetailView):
    template_name = "lectures/detail.html"
    model = Section
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(kwargs=kwargs)
        context["search_form"] = SearchForm(self.request.GET, self.request.FILES)
        context["search_key"] = ""
        context["timetables"] = []
        if self.request.user.is_authenticated:
            context["timetables"] = Timetable.objects.filter(user=self.request.user)
        return context


def timetable_info(request, id):
    """
    View for AJAX request for information of timetable of a user.
    :param request: AJAX request from client.
    :param id: the ID of a section.
    :return: JsonResponse with timetable data.
    """
    if request.is_ajax():
        # timetable section
        timetable_id = request.POST["timetable_id"]
        timetable = Timetable.objects.get(id=timetable_id)
        sections_data = []
        for section in timetable.sections.all():
            section_data = {
                "title": section.course.title,
                "times": []
            }
            for time in section.times.all():
                time_data = {
                    "day": time.day,
                    "startHour": time.start_time.hour,
                    "startMin": time.start_time.minute,
                    "endHour": time.end_time.hour,
                    "endMin": time.end_time.minute
                }
                section_data["times"].append(time_data)
            sections_data.append(section_data)

        # current section
        section_id = request.POST["section_id"]
        section = Section.objects.get(id=section_id)
        section_data = {
            "title": section.course.title,
            "times": []
        }
        for time in section.times.all():
            time_data = {
                "day": time.day,
                "startHour": time.start_time.hour,
                "startMin": time.start_time.minute,
                "endHour": time.end_time.hour,
                "endMin": time.end_time.minute
            }
            section_data["times"].append(time_data)

        data = {
            "sections": sections_data,
            "tempSection": section_data
        }
        return JsonResponse(data)


def add_class(request, id):
    """
    View for AJAX request to add a current section.
    :param request: AJAX request from client
    :param id: the ID of a section.
    :return: JsonResponse with data. The data has a url for redirection and
        the result of addition of the section in the timetable.
    """
    if request.is_ajax():
        data = {
            "url": request.build_absolute_uri(reverse('lectures:detail', args=(id,)))
        }
        if request.POST["selected_timetable_id"] == 'null':
            data["nothing"] = True
        else:
            section = Section.objects.get(id=id)
            timetable = Timetable.objects.get(id=request.POST["selected_timetable_id"])
            timetable.sections.add(section)
            data["nothing"] = False

        return JsonResponse(data)
