from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from genphen.models import EpidemCutoffValue, Drug


class EpidemCutoffValueResource(resources.ModelResource):
    """GeneDrugResistanceAssociation model import resource."""


    drug = fields.Field(
        column_name="Drug",
        attribute="drug",
        widget=ForeignKeyWidget(Drug, field="drug_name"),
    )

    medium_name = fields.Field(
        column_name="Medium",
        attribute="medium_name"
    )

    value = fields.Field(
        column_name="Value",
        attribute="value"
    )

    class Meta:
        """VariantGradeResource settings."""

        model = EpidemCutoffValue
        exclude = ("id",)
        import_id_fields = ("drug", "medium_name", "value")

class EpidemCutoffValueAdmin(ImportExportModelAdmin):
    """VariantGrade model admin panel definition."""

    resource_classes = [EpidemCutoffValueResource]

admin.site.register(
    EpidemCutoffValue,
    EpidemCutoffValueAdmin,
)