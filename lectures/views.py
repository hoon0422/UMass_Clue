from django.views import generic
from .models import *
from lectures.forms import *
from timetable.models import Timetable
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Case, When, Value


class IndexView(generic.TemplateView):
    template_name = "lectures/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(kwargs=kwargs)
        context["search_form"] = SearchForm(self.request.GET, self.request.FILES)
        context["detailed_search_form"] = DetailedSearchForm(self.request.GET, self.request.FILES)
        return context


class SearchView(generic.ListView):
    template_name = "lectures/search.html"
    context_object_name = "sections"
    paginate_by = 10

    def get_queryset(self):
        option = self.get_search_option().lower()
        if option == "course":
            courses = SearchView.search_course(self.get_search_key())
        elif option == "professor":
            courses = SearchView.search_professor(self.get_search_key())
        elif option == "room":
            courses = SearchView.search_room(self.get_search_key())
        else:
            courses = []

        return courses.order_by("-course__year_and_semester", "course__category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(kwargs=kwargs)
        context["search_form"] = SearchForm(self.request.GET, self.request.FILES)
        context["search_key"] = self.get_search_key()
        return context

    def get_search_option(self):
        key = self.get_search_key()
        idx = key.rfind('#')

        if idx == -1:
            return "Course"

        return key[idx + 1:].strip()

    def get_search_key(self):
        return self.request.GET["search_key"]

    @staticmethod
    def search_course(course_key):
        sections = Section.objects.filter(course__title__icontains=course_key)
        sorted(sections, key=lambda section: section.course.title.find(course_key))
        # TODO: Bug - sorting with relevance works, but sorting with alphabetic order after relevance required
        return sections

    @staticmethod
    def search_professor(professor_key):
        sections = Section.objects.filter(professors__name__icontains=professor_key)
        sorted(sections, key=lambda section: section.course.title.find(professor_key))
        return sections

    @staticmethod
    def search_room(room_key):
        sections = Section.objects.filter(room__name__icontains=room_key)
        sorted(sections, key=lambda section: section.course.title.find(room_key))
        return sections


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