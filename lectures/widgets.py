""" Widgets for search

This module has widgets to search lectures.

"""

import django.forms as forms
from .models import *
from django.utils.html import mark_safe


class CourseTitleInput(forms.TextInput):
    """
    Text input for the search with course title.
    """
    def __init__(self):
        super().__init__(attrs={'placeholder': 'Enter course title...'})


class ClassNumberInput(forms.TextInput):
    """
    Text input for the search with class number.
    """
    def __init__(self):
        super().__init__(attrs={'placeholder': 'Enter class number...'})


class ProfessorInput(forms.TextInput):
    """
    Text input for the search with professor.
    """
    def __init__(self):
        super().__init__(attrs={'placeholder': "Enter professor's name..."})


class CourseNumberChoice(forms.Select):
    """
    Select widget for the search with course number.
    """
    pass


class YearAndSemesterSelect(forms.Select):
    """
    Select widget for the search with year and semester.
    """
    pass


class DaySelect(forms.Select):
    """
    Select widget for the search with day.
    """
    def __init__(self, attrs=None):
        choices = [
            ('null', 'Day'),
            ('Mo', 'Mo'),
            ('Tu', 'Tu'),
            ('We', 'We'),
            ('Th', 'Th'),
            ('Fr', 'Fr'),
            ('Sa', 'Sa'),
            ('Su', 'Su')
        ]
        super().__init__(attrs=attrs, choices=choices)


def _make_hour_choices(start, end):
    """
    Return a list of choices for hour criteria.
    :param start: the first hour of choices.
    :param end: the last hour of choices.
    :return: a list of choices from start to end at intervals of an hour.
    """
    result = []
    for i in range(start, end):
        result.append((i, str(i)))
    return result


class HourSelect(forms.Select):
    """
    Select widget for the search with hour.
    """
    def __init__(self, attrs=None):
        choices = _make_hour_choices(6, 20)
        super().__init__(attrs=attrs, choices=choices)


class MinuteSelect(forms.Select):
    """
    Select widget for the search with minute.
    """
    def __init__(self, attrs=None):
        choices = [
            (0, '00'),
            (10, '10'),
            (20, '20'),
            (30, '30'),
            (40, '40'),
            (50, '50'),
        ]
        super().__init__(attrs=attrs, choices=choices)


class TimeSearchWidget(forms.MultiWidget):
    """
    Widget for the search with time. It consists of multiple widgets.
        - DaySelect: select day.
        - HourSelect: select start hour.
        - MinuteSelect: select start minute.
        - HourSelect: select end hour.
        - MinuteSelect: select end minute.
    """
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

    def render(self, name, value, attrs=None, renderer=None):
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            output.append(widget.render(name + '_%s' % i, widget_value, final_attrs))

        # return sub-widgets in this widget for the template.
        return [mark_safe(self.format_value(x)) for x in output]
