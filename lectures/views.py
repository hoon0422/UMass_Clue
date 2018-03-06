from django.shortcuts import render
from .models import *
from lectures.forms import *


def index(request):
    form = SearchForm(request.POST, request.FILES)
    context = {"form": form}
    return render(request, "lectures/index.html", context)


def search(request):
    courses = []
    data = request.POST
    form = SearchForm(request.POST, request.FILES)

    if data["search_option"] == "Course":
        courses = search_course(data["search_key"])
    elif data["search_option"] == "Professor":
        courses = search_professor(data["search_key"])
    elif data["search_option"] == "Room":
        courses = search_room(data["search_key"])

    context = {"courses": courses, "form": form}
    return render(request, "lectures/search.html", context)


def search_course(course_key):
    return Course.objects.filter(title__contains=course_key)


def search_professor(professor_key):
    return Course.objects.filter(session__professors__name__contains=professor_key)


def search_room(building_key):
    return Course.objects.filter(session__room__name__contains=building_key)

# Create your views here.
