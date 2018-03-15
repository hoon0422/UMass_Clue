from django.db import models


class Career(models.Model):
    title = models.CharField(max_length=15, null=False)


class Major(models.Model):
    title = models.CharField(max_length=30, null=False)


class Category(models.Model):
    title = models.CharField(max_length=20, null=False)


class YearAndSemester(models.Model):
    year = models.PositiveSmallIntegerField(null=False)
    semester = models.CharField(max_length=10, null=False)


class Course(models.Model):
    title = models.CharField(max_length=50, null=False)
    course_num = models.CharField(max_length=10, null=False)
    major = models.ForeignKey(Major, null=False, on_delete=models.DO_NOTHING)
    career = models.ForeignKey(Career, null=False, on_delete=models.DO_NOTHING)
    category = models.ForeignKey(Category, null=False, on_delete=models.DO_NOTHING)
    year_and_semester = models.ForeignKey(YearAndSemester, on_delete=models.DO_NOTHING, null=False)


class Professor(models.Model):
    name = models.CharField(max_length=50, null=False, primary_key=True)


class Room(models.Model):
    name = models.CharField(max_length=50, null=False)


class DayTimeField(models.Model):
    day = models.CharField(max_length=2, null=False)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=False)


class Section(models.Model):
    class_num = models.CharField(max_length=5, null=False, primary_key=True)
    professors = models.ManyToManyField(Professor)
    room = models.ForeignKey(Room, on_delete=models.DO_NOTHING, null=False)
    times = models.ManyToManyField(DayTimeField)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False)
    components = models.ManyToManyField(Category)
    upper_unit = models.FloatField(null=False)
    lower_unit = models.FloatField(null=False)
