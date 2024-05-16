from django import forms
from .models import *

class DateInputForm(forms.Form):

    date1 = forms.DateTimeField(label='От',required=False)
    date2 = forms.DateTimeField(label='До', required=False)

    date1 = forms.DateField(widget=forms.widgets.DateInput(
        attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd (DOB)', 'class': 'form-control' , 'label':'От'})
    )
    date2 = forms.DateField(widget=forms.widgets.DateInput(
        attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd (DOB)', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(DateInputForm, self).__init__(*args, **kwargs)
        self.fields['date1'].label = "От"
        self.fields['date2'].label = "До"

class CountyInputForm(forms.Form):
    country1 = forms.CharField(label='Страна №1',strip=False, required=False)
    country2 = forms.CharField(label='Страна №2',strip=False, required=False)
    country3 = forms.CharField(label='Страна №3',strip=False, required=False)
    country4 = forms.CharField(label='Страна №4',strip=False, required=False)
    country5 = forms.CharField(label='Страна №5',strip=False, required=False)

