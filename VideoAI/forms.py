# forms.py

from django import forms
from .models import ImageModel
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class TextInputForm(forms.Form):
    text_input = forms.CharField(max_length=10000, widget=forms.Textarea(attrs={'rows':25, 'cols':50}))

class ImageForm(forms.ModelForm):
    username = forms.CharField(max_length=2732)
    class Meta:
        model = ImageModel
        fields = ['image']

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
