""" Views for the app

This module has views for "timetable" app.

"""
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models
from lectures.forms import SearchForm
from accounts.models import User
from timetable.models import Timetable
from django.urls import reverse
from django.http import JsonResponse


class TimetableView(LoginRequiredMixin, generic.TemplateView):
    """ View for timetable page. """
    template_name = 'timetable/test_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # form for search
        context["search_form"] = SearchForm(self.request.GET, self.request.FILES)

        # list of timetables
        context['timetables'] = models.Timetable.objects.filter(user=self.request.user)

        # a timetable to display
        context['current_timetable'] = self.get_timetable_to_display()
        return context

    def get_timetable_to_display(self):
        """
        Find what timetable to be displayed.
        :return: Timetable to be displayed. If there is no timetable to display, return None.
        """
        if len(models.Timetable.objects.filter(user=self.request.user)) is 0:
            return None

        try:
            id_for_display = self.kwargs['id']
            return models.Timetable.objects.get(id=id_for_display)
        except KeyError:
            for timetable in models.Timetable.objects.filter(user=self.request.user):
                if timetable.default:
                    return timetable
        except models.Timetable.DoesNotExist:
            return None


def add_new_timetable(request, current_timetable_id):
    """
    View function for AJAX request to add a new timetable.
    :param request: AJAX request from client
    :param current_timetable_id: ID of the currently displayed timetable.
    :return: JsonResponse containing url for redirection.
    """
    if request.is_ajax():
        title = request.POST["title"]
        username = request.POST["username"]
        user = User.objects.get(username=username)
        new_timetable = Timetable.objects.create(title=title, user=user)

        data = {
            'url': request.build_absolute_uri(reverse("timetable:timetable_test", args=(new_timetable.id, )))
        }

        return JsonResponse(data)


def remove_timetable(request, current_timetable_id):
    """
    View function for AJAX request to remove a timetable.
    :param request: AJAX request from client
    :param current_timetable_id: ID of the currently displayed timetable.
    :return: JsonResponse containing url for redirection.
    """
    if request.is_ajax():
        id_for_remove = request.POST["id"]
        Timetable.objects.get(id=id_for_remove).delete()

        if current_timetable_id != int(id_for_remove):
            data = {
                'url': request.build_absolute_uri(reverse("timetable:timetable_test", args=(current_timetable_id,)))
            }
        else:
            data = {
                'url': request.build_absolute_uri(reverse("timetable:timetable_test_default"))
            }

        return JsonResponse(data)
