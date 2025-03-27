from django import forms

CHOICES = [
    ('1', 'Конвертировать PDF в WORD'),
    ('2', 'Распознать текст (до 5 страниц)'),
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
