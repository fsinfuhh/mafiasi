from django import forms
from django.utils.translation import ugettext as _

from mafiasi.teaching.models import Course, Teacher


class GProtBasicForm(forms.Form):
    course = forms.MultipleChoiceField()
    exam_date = forms.DateField()
    examiner = forms.MultipleChoiceField()

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        self.fields['examiner'].choices = \
            Teacher.objects.as_grouped_choices()
        self.fields['course'].choices = \
            Course.objects.as_grouped_choices()

    def clean_course(self):
        data = self.cleaned_data['course'][0]
        try:
            data = int(data)
        except ValueError:
            raise forms.ValidationError(_("Invalid course selection"))
        try:
            data = Course.objects.get(pk=data)
        except Course.DoesNotExist:
            raise forms.ValidationError(_("Selected course does not exist"))
        return data

    def clean_examiner(self):
        data = self.cleaned_data['examiner']
        result = []
        for elem in data:
            try:
                elem = int(elem)
            except ValueError:
                raise forms.ValidationError(_("Invalid examiner selection"))
            try:
                elem = Teacher.objects.get(pk=elem)
            except Course.DoesNotExist:
                raise forms.ValidationError(_("Selected examiner does not exist"))
            result.append(elem)
        return result


class GProtCreateForm(GProtBasicForm):
    type = forms.ChoiceField(choices=[('html', _('Write online')),
                                      ('pdf', _('Upload PDF'))])
