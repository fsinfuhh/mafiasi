from django import forms

from mafiasi.teaching.models import Course, Teacher

class GProtBasicForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects)
    exam_date = forms.DateField()
    examiner = forms.ModelChoiceField(queryset=Teacher.objects)
