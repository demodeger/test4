from django import forms
from .models import Option

class PollForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['votes']
