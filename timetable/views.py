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
        return context
