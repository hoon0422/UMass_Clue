from .widgets import *


class SearchForm(forms.Form):
    search_key = forms.CharField(
        label="",
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search'
        }),
        required=False)


class CourseNumberChoiceField(forms.ChoiceField):
    widget = CourseNumberChoice


class YearAndSemesterChoiceField(forms.ChoiceField):
    widget = YearAndSemesterSelect


class DayChoiceField(forms.ChoiceField):
    widget = DaySelect


class HourChoiceField(forms.ChoiceField):
    widget = HourSelect


class MinuteChoiceField(forms.ChoiceField):
    widget = MinuteSelect


class CourseTitleCharField(forms.CharField):
    widget = CourseTitleInput
    pass


class ClassNumberCharField(forms.CharField):
    widget = ClassNumberInput
    pass


class ProfessorCharField(forms.CharField):
    widget = ProfessorInput
    pass


class TimeSearchField(forms.MultiValueField):
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
    CHOICES = [
        ('course_title', 'Course title'),
        ('course_number', 'Course number'),
        ('class_number', 'Class number'),
        ('professor', 'Professor'),
        ('year_and_semester', 'Semester'),
        ('time', 'Time')
    ]
    search_option = forms.ChoiceField(choices=CHOICES, widget=forms.Select(attrs={
        'id': 'search_option',
        'onchange': 'searchOptionChange()'
    }))
    course_title = CourseTitleCharField()
    course_number = CourseNumberChoiceField(choices=[
        (str(cn), str(cn)) for cn in Course.objects.values('course_num').distinct().order_by('course_num')
    ])
    class_number = ClassNumberCharField()
    professor = ProfessorCharField()
    year_and_semester = YearAndSemesterChoiceField(choices=[
        (str(ys), str(ys)) for ys in YearAndSemester.objects.all()
    ])
    time = TimeSearchField()
