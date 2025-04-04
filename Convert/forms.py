from django import forms

CHOICES = [
    ('1', 'Конвертировать PDF в WORD (до 100 страниц)'),
    ('2', 'Распознать текст (до 3 страниц)'),
]

class UploadFileForm(forms.Form):
    # title = forms.CharField(max_length=500)
    file = forms.FileField()
    choice = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.RadioSelect,
        label="Выбери опцию",
        required=True
    )
