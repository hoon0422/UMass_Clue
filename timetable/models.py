from django.db import models
from lectures.models import Section


class Timetable(models.Model):
    title = models.CharField(max_length=20, null=False)
    sections = models.ManyToManyField(Section)

    def __str__(self):
        return self.title
