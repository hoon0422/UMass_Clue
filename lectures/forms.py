from django import forms
from .models import YearAndSemester, Course


class SearchForm(forms.Form):
    search_key = forms.CharField(
        label="",
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search'
        }),
        required=False)


class SearchInput:
    pass


class CourseTitleInput(SearchInput, forms.TextInput):
    pass


class CourseNumberInput(SearchInput, forms.Select):
    choices = [
        (cn, cn) for cn in Course.objects.values('course_num').distinct().order_by('course_num')
    ]


class ClassNumberInput(SearchInput, forms.TextInput):
    pass


class ProfessorInput(SearchInput, forms.TextInput):
    pass


class YearAndSemesterSelect(forms.Select):
    choices = [
        (str(ys), str(ys)) for ys in YearAndSemester.objects.all()
    ]


class DaySelect(forms.Select):
    choices = [
        ('Mo', 'Mo'),
        ('Tu', 'Tu'),
        ('We', 'We'),
        ('Th', 'Th'),
        ('Fr', 'Fr'),
        ('Sa', 'Sa'),
        ('Su', 'Su')
    ]


class HourSelect(forms.Select):
    @staticmethod
    def _make_choices(start, end):
        result = []
        for i in range(start, end):
            result.append((i, str(i)))
        return result

    choices = _make_choices(6, 20)


class MinuteSelect(forms.Select):
    choices = [
        (0, '00'),
        (10, '10'),
        (20, '20'),
        (30, '30'),
        (40, '40'),
        (50, '50'),
    ]


class TimeSearchWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            DaySelect(attrs={'id': 'select_day'}),
            HourSelect(attrs={'id': 'select_start_hour'}),
            MinuteSelect(attrs={'id': 'select_start_minute'}),
            HourSelect(attrs={'id': 'select_end_hour'}),
            MinuteSelect(attrs={'id': 'select_end_minute'})
        )
        super(TimeSearchWidget, self).__init__(widgets, attrs=attrs)

    def decompress(self, value):
        return [value.day, value.start_hour, value.start_minute, value.end_hour, value.end_min] if value \
            else [None, None, None, None, None]


class DetailedSearchForm(forms.Form):
    CHOICES = [
        ('course_title', 'Course title'),
        ('course_number', 'Course number'),
        ('class_number', 'Class number'),
        ('professor', 'Professor'),
        ('year_and_semester', 'Semester'),
        ('time', 'Time')
    ]
    search_option = forms.Select(choices=CHOICES, attrs={'id': 'search_option'})
    course_title = CourseTitleInput(attrs={'placeholder': 'Enter course title...'})
    course_number = CourseNumberInput(attrs={'placeholder': 'Enter course number...'})
    class_number = ClassNumberInput(attrs={'placeholder': 'Enter class number...'})
    professor = ProfessorInput(attrs={'placeholder': "Enter professor's name..."})
    year_and_semester = YearAndSemesterSelect(attrs={'placeholder': 'Year Semester'})
    time = TimeSearchWidget()
