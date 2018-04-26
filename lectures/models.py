""" Module for models about lectures """

from django.db import models


class Career(models.Model):
    """ Represents a career.

    Comparison criteria: dictionary order of title.

    Attributes:
        title: the title of a career.
    """
    title = models.CharField(max_length=15, null=False)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Career instance must be compared with Career instance.")
        return self.title < other.title

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Career instance must be compared with Career instance.")
        return not self == other and not self < other

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Career instance must be compared with Career instance.")
        return not self > other

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Career instance must be compared with Career instance.")
        return not self < other


class Major(models.Model):
    """ Represents a major.

    Comparison criteria: dictionary order of title.

    Attributes:
        title: the name of the major.
    """
    title = models.CharField(max_length=30, null=False)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Major instance must be compared with Major instance.")
        return self.title < other.title

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Major instance must be compared with Major instance.")
        return not self == other and not self < other

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Major instance must be compared with Major instance.")
        return not self > other

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Major instance must be compared with Major instance.")
        return not self < other


class Category(models.Model):
    """ Represents a category of a section.

    Comparison criteria:
        if there is a key in category_map, then follow it. If not, the priority is the latest.

    Attributes:
        title: the title of category.
        category_map: dictionary for comparison.

    """
    title = models.CharField(max_length=20, null=False)
    category_map = {
        "Lecture": 0,
        "Laboratory": 1
    }

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Category instance must be compared with Category instance.")
        try:
            self_priority = self.category_map[self.title]
        except KeyError:
            self_priority = len(self.category_map)

        try:
            other_priority = self.category_map[other.title]
        except KeyError:
            other_priority = len(self.category_map)
        if self_priority != other_priority:
            return self_priority < other_priority
        return self.title < other.title

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Category instance must be compared with Category instance.")
        return not self == other and not self < other

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Category instance must be compared with Category instance.")
        return not self > other

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Category instance must be compared with Category instance.")
        return not self < other


class YearAndSemester(models.Model):
    """ Represents year and semester of a section.

    Comparison criteria: follow semester_map.

    Attributes:
        year: year data (4 digits)
        semester: semester data (Spring, Summer, Fall, Winter)

    """
    year = models.PositiveSmallIntegerField(null=False)
    semester = models.CharField(max_length=10, null=False)
    semester_map = {
        "Spring": 0,
        "Summer": 1,
        "Fall": 2,
        "Winter": 3
    }

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("YearAndSemester instance must be compared with YearAndSemester instance.")
        if self.year != other.year:
            return self.year < other.year
        return self.semester_map[self.semester] < self.semester_map[other.semester]

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("YearAndSemester instance must be compared with YearAndSemester instance.")
        return not self == other and not self < other

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("YearAndSemester instance must be compared with YearAndSemester instance.")
        return not self > other

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("YearAndSemester instance must be compared with YearAndSemester instance.")
        return not self < other

    def __str__(self):
        return str(self.year) + ' ' + self.semester


class Course(models.Model):
    """ Represents a course.

    Attributes:
        title: the course title.
        course_num: the course number (<major key> <some alphanumeric characters>).
        major: the major of a course.
        career: the career of a course.
        category: the category of a course.
        year_and_semester: the year and semester of a course.
    """
    title = models.CharField(max_length=50, null=False)
    course_num = models.CharField(max_length=10, null=False)
    major = models.ForeignKey(Major, null=False, on_delete=models.DO_NOTHING)
    career = models.ForeignKey(Career, null=False, on_delete=models.DO_NOTHING)
    category = models.ForeignKey(Category, null=False, on_delete=models.DO_NOTHING)
    year_and_semester = models.ForeignKey(YearAndSemester, on_delete=models.DO_NOTHING, null=False)


class Professor(models.Model):
    """ Represents a professor.

    Comparison criteria: dictionary order of name.

    Attributes:
        name: the name of a professor.

    """
    name = models.CharField(max_length=50, null=False, primary_key=True)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Professor instance must be compared with Professor instance.")
        return self.name < other.name

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Professor instance must be compared with Professor instance.")
        return not self == other and not self < other

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Professor instance must be compared with Professor instance.")
        return not self > other

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Professor instance must be compared with Professor instance.")
        return not self < other


class Room(models.Model):
    """ Represents a room data.

    Comparison criteria: dictionary order of name.

    Attributes:
        name: the name of the room.

    """
    name = models.CharField(max_length=50, null=False)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Room instance must be compared with Room instance.")
        return self.name < other.name

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Room instance must be compared with Room instance.")
        return not self == other and not self < other

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Room instance must be compared with Room instance.")
        return not self > other

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Room instance must be compared with Room instance.")
        return not self < other


class DayTimeField(models.Model):
    """ Represents a time unit of a section.

    Comparison criteria:
        1. day (Mo < Tu < We < Th < Fr < Sa < Su)
        2. start_time
        3. end_time

    Attributes:
        day: the day of a time unit.
        start_time: the start time of a time unit.
        end_time: the end time of a time unit.
        day_map: the map for day comparison.

    """
    day = models.CharField(max_length=2, null=False)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=False)
    day_map = {
        "Mo": 0,
        "Tu": 1,
        "We": 2,
        "Th": 3,
        "Fr": 4,
        "Sa": 5,
        "Su": 6,
    }

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("DayTimeField instance must be compared with DayTimeField instance.")
        if self.day != other.day:
            return self.day_map[self.day] < self.day_map[other.day]
        if self.start_time != other.start_time:
            return self.start_time < other.start_time
        return self.end_time < other.end_time

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("DayTimeField instance must be compared with DayTimeField instance.")
        return not self == other and not self < other

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("DayTimeField instance must be compared with DayTimeField instance.")
        return not self > other

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("DayTimeField instance must be compared with DayTimeField instance.")
        return not self < other


class Section(models.Model):
    """ Represents a section.

    Attributes:
        class_num: the 5-digit number. Primary key of a section in SPIRE.
        professors: the professors teaching in a section (many to many relationship with 'Professor').
        room: the room of a section.
        times: the time units of a section (many to many relationship with "DayTimeField").
        course: the course of a section.
        components: the components of a section (many to many relationship with "Category").
        upper_unit: the upper unit of a section.
        lower_unit: the lower unit of a section.

    """
    class_num = models.CharField(max_length=5, null=False)
    professors = models.ManyToManyField(Professor)
    room = models.ForeignKey(Room, on_delete=models.DO_NOTHING, null=False)
    times = models.ManyToManyField(DayTimeField)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False)
    components = models.ManyToManyField(Category)
    upper_unit = models.FloatField(null=False)
    lower_unit = models.FloatField(null=False)
