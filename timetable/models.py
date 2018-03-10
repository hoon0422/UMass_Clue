from django.db import models
from lectures.models import Session


class Timetable(models.Model):
    title = models.CharField(max_length=20, null=False)
    sessions = models.ManyToManyField(Session)

    def __str__(self):
        return self.title
