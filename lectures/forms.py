""" Forms for search

This module has classes for field and forms for search.

"""

from .widgets import *


class SearchForm(forms.Form):
    """
    Basic form for search. It will be located on the top menu bar.
    """
    search_key = forms.CharField(
        label="",
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search'
        }),
        required=False)


class CourseNumberChoiceField(forms.ChoiceField):
    """
    Choice field for course numbers.
    """
    widget = CourseNumberChoice


class YearAndSemesterChoiceField(forms.ChoiceField):
    """
    Choice field for years and semesters.
    """
    widget = YearAndSemesterSelect


class DayChoiceField(forms.ChoiceField):
    """
    Choice field for days.
    """
    widget = DaySelect


class HourChoiceField(forms.ChoiceField):
    """
    Choice field for hours.
    """
    widget = HourSelect


class MinuteChoiceField(forms.ChoiceField):
    """
    Choice field for minutes.
    """
    widget = MinuteSelect


class CourseTitleCharField(forms.CharField):
    """
    CharField for course title.
    """
    widget = CourseTitleInput
    pass


class ClassNumberCharField(forms.CharField):
    """
    CharField for class number.
    """
    widget = ClassNumberInput
    pass


class ProfessorCharField(forms.CharField):
    """
    CharField for professor.
    """
    widget = ProfessorInput
    pass


class TimeSearchField(forms.MultiValueField):
    """
    Field for time search. It has five subfields.
        - DayChoiceField for day.
        - HourChoiceField for start hour.
        - MinuteChoiceField for start minute.
        - HourChoiceField for end hour.
        - MinuteChoiceField for end minute.
    """
    widget = TimeSearchWidget

    def __init__(self, *args, **kwargs):
        fields = [
            DayChoiceField(),
            HourChoiceField(),
            MinuteChoiceField(),
            HourChoiceField(),
            MinuteChoiceField()
        ]
        super().__init__(fields, **kwargs)

    def compress(self, data_list):
        return data_list


class DetailedSearchForm(forms.Form):
    """ Form for detailed search.

    This form is for detailed search of sections. Each attribute is an option for search.

    Attributes:
        course_title: field for course title.
        course_number: field for course number.
        class_number: field for class number.
        professor: field for professor.
        year_and_semester: field for year and semester.
        time: field for time.

    """
    course_title = CourseTitleCharField(label='Course Title')
    course_number = CourseNumberChoiceField(label='Course Number', choices=[('null', 'Course Number')] + [
        (str(cn['course_num']), str(cn['course_num'])) \
        for cn in Course.objects.values('course_num').distinct().order_by('course_num')
    ])
    class_number = ClassNumberCharField(label='Class Number')
    professor = ProfessorCharField(label='Professor')
    year_and_semester = YearAndSemesterChoiceField(label='Year & Semester', choices=[('null', 'Year & Semester')] + [
        (str(ys), str(ys)) for ys in YearAndSemester.objects.all()
    ])
    time = TimeSearchField(label='Time')
