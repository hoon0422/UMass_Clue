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
