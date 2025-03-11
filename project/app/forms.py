from django import forms
from .models import MediaFile

class FormSubmissionForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['status','remarks']