from django.db import models


class Professor(models.Model):
    name = models.CharField(max_length=50, null=False)


class Building(models.Model):
    name = models.CharField(max_length=50, null=False)
    gps = models.CharField(max_length=50, null=True)


class YearAndSemester(models.Model):
    year = models.PositiveSmallIntegerField()
    semester = models.PositiveSmallIntegerField()


class DayTimeField(models.Model):
    day = models.CharField(max_length=2, null=False)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=False)


class Lecture(models.Model):
    title = models.CharField(max_length=50, null=False)
    professors = models.ManyToManyField(Professor, on_delete=models.DO_NOTHING, null=False)
    building = models.ForeignKey(Building, on_delete=models.DO_NOTHING, null=False)
    days = models.ManyToManyField(DayTimeField, on_delete=models.DO_NOTHING, null=False)
    year_and_semester = models.ForeignKey(YearAndSemester, on_delete=models.DO_NOTHING, null=False)