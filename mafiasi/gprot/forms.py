from functools import partial
from django import forms
from django.utils.translation import ugettext as _

from mafiasi.gprot.models import Label
from mafiasi.teaching.models import Course, Teacher


def pk_to_object(Model, elem, error_msg=''):
    try:
        elem = int(elem)
        elem = Model.objects.get(pk=elem)
    except (Course.DoesNotExist, ValueError):
        raise forms.ValidationError(error_msg)
    return elem

class GProtSearchForm(forms.Form):
    search = forms.MultipleChoiceField()

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        def modify_ids(prefix, elem):
            # elem is either of the form (pk, name) or
            # (department, [(pk, name), (pk, name), ...])
            first, second = elem
            if type(second) == list:  # (department, [(pk, name), (pk, name), ...])
                return first, [('{}-{}'.format(prefix, pk), name)
                                    for pk, name in second]
            else:  # (pk, name)
                return '{}-{}'.format(prefix, first), second
        modify_examiners = partial(modify_ids, 'e')
        modify_courses = partial(modify_ids, 'c')

        examiner_groups = Teacher.objects.as_grouped_choices()
        course_groups = Course.objects.as_grouped_choices()

        self.fields['search'].choices = \
            [modify_examiners(e) for e in examiner_groups] \
          + [modify_courses(c) for c in course_groups]

    def clean_search(self):
        data = self.cleaned_data['search']
        examiners = []
        courses = []
        for elem in data:
            if elem.startswith('e-'):
                examiners.append(pk_to_object(Teacher, elem[2:],
                                        _("Selected examiner does not exist")))
            elif elem.startswith('c-'):
                courses.append(pk_to_object(Course, elem[2:],
                                        _("Selected course does not exist")))
            else:
                raise forms.ValidationError(_("Invalid selection"))
        return examiners, courses


class GProtBasicForm(forms.Form):
    course = forms.MultipleChoiceField()
    exam_date = forms.DateField()
    examiner = forms.MultipleChoiceField()
    labels = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False)

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        self.fields['examiner'].choices = \
            Teacher.objects.as_grouped_choices()
        self.fields['course'].choices = \
            Course.objects.as_grouped_choices()
        self.fields['labels'].choices = Label.objects.as_choices()

    def clean_course(self):
        data = self.cleaned_data['course'][0]
        return pk_to_object(Course, data,
                            _("Selected course does not exist"))


    def clean_examiner(self):
        data = self.cleaned_data['examiner']
        result = []
        for elem in data:
            result.append(pk_to_object(Teacher, elem,
                                       _("Selected examiner does not exist")))
        return result


class GProtCreateForm(GProtBasicForm):
    type = forms.ChoiceField(choices=[('html', _('Write online')),
                                      ('pdf', _('Upload PDF'))])
