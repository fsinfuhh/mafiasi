import django.forms as forms

from mafiasi.teaching.models import Course, Department, Teacher


class DepartmentFieldMixin:
    def initialize_department_field(self):
        self.fields["department"].choices = Department.objects.as_grouped_choices()

    def clean_department(self):
        data = self.cleaned_data["department"]
        try:
            pk = int(data)
            dep = Department.objects.get(pk=pk)
        except:
            raise forms.ValidationError("Invalid department")
        return dep


class TeacherForm(forms.ModelForm, DepartmentFieldMixin):
    department = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.initialize_department_field()

    class Meta:
        model = Teacher
        fields = ["first_name", "last_name", "title", "department"]


class CourseForm(forms.ModelForm, DepartmentFieldMixin):
    department = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.initialize_department_field()

    class Meta:
        model = Course
        fields = ["name", "short_name", "department"]
