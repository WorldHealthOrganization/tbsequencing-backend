from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from genphen.models import PDSTestCategory, Drug, GrowthMedium, PDSAssessmentMethod


class PDSTestCategoryResource(resources.ModelResource):
    """GeneDrugResistanceAssociation model import resource."""


    drug = fields.Field(
        column_name="Drug",
        attribute="drug",
        widget=ForeignKeyWidget(Drug, field="drug_name"),
    )

    medium = fields.Field(
        column_name="Medium",
        attribute="medium",
        widget=ForeignKeyWidget(GrowthMedium, field="medium_name"),
    )

    method = fields.Field(
        column_name="Method",
        attribute="method",
        widget=ForeignKeyWidget(PDSAssessmentMethod, field="method_name"),
    )

    concentration = fields.Field(
        column_name="Concentration",
        attribute="concentration"
    )

    category = fields.Field(
        column_name="Category",
        attribute="category"
    )


    class Meta:
        """VariantGradeResource settings."""

        model = PDSTestCategory
        exclude = ("id",)
        import_id_fields = ("drug", "medium", "method", "concentration", "category")

class PDSTestCategoryAdmin(ImportExportModelAdmin):
    """VariantGrade model admin panel definition."""

    resource_classes = [PDSTestCategoryResource]

admin.site.register(
    PDSTestCategory,
    PDSTestCategoryAdmin,
)
