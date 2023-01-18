from django.utils.translation import gettext_lazy as _

from mafiasi.base.base_apps import BaseService


class GprotConfig(BaseService):
    default = True
    name = "mafiasi.gprot"
    verbose_name = "GProt"
    title = _("GProt")
    description = _("The GProt contains memory minutes of oral and written exams.")
    link = "/gprot/"
    image = "img/services/gprot.svg"
