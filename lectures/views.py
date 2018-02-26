from django.shortcuts import render
from .models import *


def index(request):
    lectures = Lecture.objects.all()
    context = {'lectures': lectures}
    return render(request, "lectures/index.html", context)


def search_lecture(request, lecture_key):
    lectures = Lecture.objects.filter(title__contains=lecture_key)
    context = {'lectures': lectures}
    return render(request, "lectures/index.html", context)


def search_professor(request, professor_key):
    professors = Professor.objects.filter(name__contains=professor_key)
    lectures = []
    for professor in professors:
        lectures = lectures + professor.lecture_set
    context = {'lectures': lectures}
    return render(request, "lectures/index.html", context)


def search_building(request, building_key):
    buildings = Building.objects.filter(name__contains=building_key)
    lectures = []
    for building in buildings:
        lectures = lectures + building.lecture_set
    context = {'lectures': lectures}
    return render(request, "lectures/index.html", context)


# Create your views here.
