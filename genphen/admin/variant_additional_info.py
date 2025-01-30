from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin

from genphen.models import VariantAdditionalInfo


class VariantAdditionalInfoResource(resources.ModelResource):
    """VariantGrade model import resource."""

    position = fields.Field(column_name="Position", attribute="position")

    alternative_nucleotide = fields.Field(
        column_name="AlternativeNucleotide",
        attribute="alternative_nucleotide",
    )

    reference_nucleotide = fields.Field(
        column_name="ReferenceNucleotide",
        attribute="reference_nucleotide",
    )

    v1_annotation = fields.Field(column_name="V1", attribute="v1_annotation")

    class Meta:
        """VariantLineageAssociationResource settings."""

        model = VariantAdditionalInfo
        exclude = ("id", "variant")
        import_id_fields = (
            "position",
            "alternative_nucleotide",
            "reference_nucleotide",
            "v1_annotation",
        )


class VariantAdditionalInfoAdmin(ImportExportModelAdmin):
    """VariantGrade model admin panel definition."""

    resource_classes = [VariantAdditionalInfoResource]
    skip_admin_log = True
    readonly_fields = ("variant",)


admin.site.register(VariantAdditionalInfo, VariantAdditionalInfoAdmin)
