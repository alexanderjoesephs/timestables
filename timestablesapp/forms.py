from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User


class CustomisedUserCreationForm(UserCreationForm):
    ACCOUNT_CHOICES = [
        ('teacher', 'Teacher Account'),
        ('student', 'Student Account'),
    ]
    
    account_type = forms.ChoiceField(choices=ACCOUNT_CHOICES)
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