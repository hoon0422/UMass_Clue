from django import forms


class SearchForm(forms.Form):
    search_key = forms.CharField(
        label="",
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'search-input'
        }),
        required=False)

    search_option = forms.ChoiceField(
        label="",
        required=False,
        choices=(
            ("Course", "Course"),
            ("Professor", "Professor"),
            ("Room", "Room")
        ),
        widget=forms.Select(attrs={
            'class': 'search-option'
        })
    )
