from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models
from lectures.forms import SearchForm


class TimetableView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'timetable/test_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm(self.request.GET, self.request.FILES)
        context['timetables'] = models.Timetable.objects.filter(user=self.request.user)
        context['current_timetable'] = self.get_timetable_to_display()
        return context

    def get_timetable_to_display(self):
        if len(models.Timetable.objects.filter(user=self.request.user)) is 0:
            return None

        try:
            id_for_display = self.request.GET['id']
            return models.Timetable.objects.get(id=id_for_display)
        except KeyError:
            for timetable in models.Timetable.objects.filter(user=self.request.user):
                if timetable.default:
                    return timetable
        except models.Timetable.DoesNotExist:
            return None
