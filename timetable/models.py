from django.db import models
from lectures.models import Section
from accounts.models import User


class Timetable(models.Model):
    title = models.CharField(max_length=20, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    sections = models.ManyToManyField(Section)
    _default = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.title

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        raise AttributeError("You cannot set 'default' attribute directly")

    def set_as_default(self):
        current_default = None
        user_timetables = Timetable.objects.filter(user=self.user)
        for i in range(len(user_timetables)):
            if user_timetables[i].default:
                current_default = user_timetables[i]
                break

        if current_default is not None:
            current_default._default = False

        self._default = True
