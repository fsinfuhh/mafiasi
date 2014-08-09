{% load i18n %}
$(function() {
    $("#id_course").select2({
        maximumSelectionSize: 1,
        placeholder: "{% trans 'Select a module' %}",
    }).select2('open');

    $("#id_examiner").select2({
        placeholder: "{% trans 'Select the examiners' %}",
    });

    $("#id_course-department, #id_teacher-department")
        .select2()
        .select2('val', 1);

    $('#id_exam_date').datepicker({
        'firstDay': 1,
        'dateFormat': 'yy-mm-dd'
    });
});

$("#add-teacher-submit").click(function () {
    $.ajax({
        type: "POST",
        url: "{% url 'teaching_api_create_teacher' %}",
        data: $("#add-teacher").serialize(),
        success: function(result) {
            var teacher = result[0];
            $("#modal-add-teacher").modal('hide');
            $('#add-teacher').trigger('reset');
            $("add-teacher-errors").hide().children().replaceWith($("<ul/>"));

            var name = [teacher.fields.title, teacher.fields.first_name, teacher.fields.last_name].join(' ');
            var option = $('<option/>').val(teacher.pk).text(name);
            var sel = $("#id_examiner").select2('val');
            sel.push(teacher.pk);
            $("#id_examiner").prepend(option).select2('val', sel);
        },
        error: function(xhr) {
            var ul = xhr.responseText;
            $("#add-teacher-errors").fadeIn().children().replaceWith(ul);
        },
    });
});

$("#add-course-submit").click(function () {
    $.ajax({
        type: "POST",
        url: "{% url 'teaching_api_create_course' %}",
        data: $("#add-course").serialize(),
        success: function(result) {
            var course = result[0];
            $("#modal-add-course").modal('hide');
            $('#add-course').trigger('reset');
            $("add-course-errors").hide().children().replaceWith($("<ul/>"));

            var name = (course.fields.short_name
                ? course.fields.name + " (" + course.fields.short_name + ")"
                : course.fields.name);
            var option = $('<option/>').val(course.pk).text(name);
            $("#id_course").prepend(option).select2('val', course.pk);
        },
        error: function(xhr) {
            var ul = xhr.responseText;
            $("#add-course-errors").fadeIn().children().replaceWith(ul);
        },
    });
});
