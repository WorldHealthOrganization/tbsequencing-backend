from datetime import date

from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from submission.models import Sample, SequencingData

from .sequencing_data_hash_inline import SequencingDataHashInline


class SequencingDataResource(resources.ModelResource):
    """Import created for CNCB specific samples."""

    library_name = fields.Field(column_name="SeqId", attribute="library_name")

    sample = fields.Field(
        column_name="BioSampleId",
        attribute="sample",
        widget=ForeignKeyWidget(Sample, field="biosample_id"),
    )

    data_location = fields.Field(column_name="DataLocation", attribute="data_location")

    file_path = fields.Field(column_name="FilePath", attribute="file_path")

    library_preparation_strategy = fields.Field(
        column_name="LibraryStrategy",
        attribute="library_preparation_strategy",
    )

    dna_source = fields.Field(column_name="LibrarySource", attribute="dna_source")

    dna_selection = fields.Field(
        column_name="LibrarySelection",
        attribute="dna_selection",
    )

    sequencing_platform = fields.Field(
        column_name="Platform",
        attribute="sequencing_platform",
    )

    library_layout = fields.Field(
        column_name="LibraryLayout",
        attribute="library_layout",
    )

    class Meta:
        """Meta class for the SequencingDataResource."""

        model = SequencingData

        exclude = (
            "filename",
            "file_size",
            "id",
            "sequencing_machine",
            "assay",
            "packages",
            "created_at",
            "s3_storage_class",
        )

        import_id_fields = (
            "sample",
            "library_name",
            "data_location",
            "file_path",
        )

    def before_save_instance(
        self, instance, row, **kwargs
    ):  # pylint: disable=unused-argument, duplicate-code
        """Set default values for the instance."""
        instance.s3_storage_class = None
        instance.created_at = date.today()


class SequencingDataAdmin(ImportExportModelAdmin):
    """Sequencing data admin page."""

    resource_classes = [SequencingDataResource]

    inlines = [SequencingDataHashInline]

    list_display = [
        "__str__",
        "get_library_url",
        # "get_filenames",
        "created_at",
    ]

    readonly_fields = [
        "file_size",
        "file_path",
        "filename",
    ]

    raw_id_fields = ["sample"]

    list_filter = [
        "data_location",
        "s3_storage_class",
    ]

    search_fields = [
        "library_name",
        "=id",
        "assoc_packages__filename",
    ]


admin.site.register(SequencingData, SequencingDataAdmin)
