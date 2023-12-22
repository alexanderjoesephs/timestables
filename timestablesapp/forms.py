from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User


class CustomisedUserCreationForm(UserCreationForm):
    Teacher_account = forms.BooleanField(required=False)
    Admin_account = forms.BooleanField(required=False)
    class Meta:
        model = User
        fields = ['username','first_name','last_name','password1','password2']



from .models import Test

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['set']
        widgets = {
            'set': forms.RadioSelect(choices=((True, 'True'), (False, 'False'))),
        }