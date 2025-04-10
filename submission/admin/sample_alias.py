from datetime import date

from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from submission.models import Package, Sample, SampleAlias


class SampleAliasResource(resources.ModelResource):
    """Import created for CNCB specific samples."""

    name = fields.Field(column_name="Name", attribute="name")

    sample = fields.Field(
        column_name="BioSampleId",
        attribute="sample",
        widget=ForeignKeyWidget(Sample, field="biosample_id"),
    )

    origin = fields.Field(column_name="Origin", attribute="origin")

    origin_label = fields.Field(column_name="Label", attribute="origin_label")

    class Meta:
        """Meta class for the SampleAliasResource."""

        model = SampleAlias

        exclude = (
            "id",
            "created_at",
            "fastq_prefix",
            "match_source",
            "package",
            "country",
            "sampling_date",
            "verdicts",
        )

        import_id_fields = (
            "sample",
            "origin",
            "origin_label",
        )

    def __init__(self, **kwargs):
        """Initialize the package field."""
        super().__init__(**kwargs)
        self.package = None

    def before_import(self, dataset, **kwargs):  # pylint: disable=unused-argument, duplicate-code
        """Create a package for the imported samples."""
        package_name = "Django package created from file uploaded via the admin panel."

        package = Package.objects.create(
            name=package_name,
            description="""
            This package was created after dataset import via the Django admin panel.
            """,
            origin="Admin",
            owner=kwargs.get("user"),
            submitted_on=date.today(),
        )

        self.package = package

        package.save()

    def before_save_instance(self, instance, row, **kwargs):  # pylint: disable=unused-argument, duplicate-code
        """Set the package and created_at fields for the imported samples."""
        instance.package = self.package
        instance.created_at = date.today()


class SampleAliasAdmin(ImportExportModelAdmin):
    """Sequencing data hash admin page."""

    resource_classes = [SampleAliasResource]

    raw_id_fields = [
        "sample",
    ]

    search_fields = [
        "name",
    ]

    verbose_name_plural = "Sample aliases"


class SampleAliasInline(admin.TabularInline):
    """Inline display in the sample view."""

    model = SampleAlias
    extra = 0
    max_num = 0
    can_delete = False
    verbose_name_plural = "Sample aliases"
    verbose_name = "Sample alias"
    show_change_link = False
    fields = ["package", "name", "origin", "origin_label", "match_source"]

    readonly_fields = ["package", "name", "origin", "origin_label", "match_source"]


admin.site.register(SampleAlias, SampleAliasAdmin)
