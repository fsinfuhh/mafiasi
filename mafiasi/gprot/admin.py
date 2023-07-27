import hashlib

from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse

from mafiasi.gprot.models import (
    Attachment,
    BlockedGprots,
    Favorite,
    GProt,
    Label,
    Notification,
    Reminder,
)

admin.site.register(Attachment)


class GProtAdmin(admin.ModelAdmin):
    list_display = ("pk", "course", "exam_date", "published", "is_pdf")
    list_display_links = ("course",)
    list_filter = ("published", "is_pdf")
    search_fields = ("course__name",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<path:object_id>/block/", self.admin_site.admin_view(self.block_view), name="gprot_block"),
        ]

        return custom_urls + urls

    def block_view(self, request, object_id):
        to_block = get_object_or_404(GProt, pk=object_id)
        if not to_block.is_pdf:
            messages.error(request, "Cannot block, not a PDF")
        else:
            to_block.published = False
            to_block.owner = None
            to_block.save()
            pdf_filefield = to_block.content_pdf
            if not pdf_filefield:
                messages.error(request, "Cannot block, no file")
            else:
                pdf_filefield.file.open()
                contents = pdf_filefield.file.read()
                pdf_filefield.file.close()
                pdf_filefield.delete()
                hash = hashlib.sha256(contents).hexdigest()
                BlockedGprots.objects.create(pdf_hash=hash, gprot_title=str(to_block), blocked_by=request.user)
                messages.success(request, "Successfully blocked")

        return redirect(reverse("admin:gprot_gprot_change", args=(object_id,)))


admin.site.register(GProt, GProtAdmin)

admin.site.register(Notification)
admin.site.register(Reminder)
admin.site.register(Label)
admin.site.register(Favorite)
admin.site.register(BlockedGprots)
