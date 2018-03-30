from django.db import models
from lectures.models import Section
from accounts.models import User


class Timetable(models.Model):
    title = models.CharField(max_length=20, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    sections = models.ManyToManyField(Section)

    def __str__(self):
        return self.title
