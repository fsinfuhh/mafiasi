from django.conf import settings
from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class TasksConfig(BaseService):
    default = True
    name = "mafiasi.tasks"
    verbose_name = "Tasks"
    title = _("Tasks")
    description = _(
        "Tasks is a task management platform that allows you to organize your tasks and projects with groups and boards."
    )
    link = settings.TASKS_URL
    image = "img/services/kanboard.svg"
