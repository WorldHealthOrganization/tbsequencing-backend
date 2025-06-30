from django.contrib import admin

from submission.models import Contributor

from import_export import resources
from import_export.admin import ImportExportModelAdmin


class ContributorResource(resources.ModelResource):
    class Meta:
        model = Contributor



class ContributorInline(admin.TabularInline):
    """Inline display in the package view."""
    model = Contributor
    extra = 0
    max_num = 0
    can_delete = False
    verbose_name_plural = "Contributors"
    verbose_name = "Contributor"
    show_change_link = False

    fields = [
        "first_name",
        "last_name",
        "role"
    ]

    readonly_fields = [
        "first_name",
        "last_name",
        "role"
    ]



@admin.register(Contributor)
class ContributorAdmin(ImportExportModelAdmin):
    """Contributor admin page."""

    resource_classes = [ContributorResource]

    readonly_fields = [
        "first_name",
        "last_name",
        "role"
    ]
