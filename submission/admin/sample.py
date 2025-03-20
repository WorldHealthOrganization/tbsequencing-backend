from datetime import date

from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from biosql.models import Taxon
from genphen.models import Country
from submission.models import Package, Sample

from .sample_alias import SampleAliasInline
from .sample_mic import MinimumInhibitoryConcentrationValueInline
from .sample_pdst import PhenotypicDrugSusceptibilityTestInline


class SampleResource(resources.ModelResource):
    """
    Import created for CNCB specific samples.

    For biosample integer, we use the negative value of
    the biosample accession name digits only.
    """

    ncbi_taxon = fields.Field(
        column_name="TaxID",
        attribute="ncbi_taxon",
        widget=ForeignKeyWidget(Taxon, field="ncbi_taxon_id"),
    )

    biosample_id = fields.Field(column_name="BioSampleId", attribute="biosample_id")

    country = fields.Field(
        column_name="Country",
        attribute="country",
        widget=ForeignKeyWidget(Country, field="three_letters_code"),
    )

    submission_date = fields.Field(
        column_name="ReleaseDate",
        attribute="submission_date",
    )

    class Meta:
        """Model options."""

        model = Sample

        exclude = (
            "id",
            "sampling_date",
            "additional_geographical_information",
            "latitude",
            "longitude",
            "isolation_source",
            "bioanalysis_status",
            "bioanalysis_status_changed_at",
            "package",
            "origin",
        )

        import_id_fields = ("biosample_id",)

    def before_import(self, dataset, **kwargs):  # pylint: disable=unused-argument, duplicate-code
        """Create a package for the imported samples."""
        package_name = "Django package created from file uploaded via the admin panel"

        package = Package.objects.create(
            name=package_name,
            description="""
            This package was created after dataset import via the Django admin panel.
            """,
            origin="Admin",
            owner=kwargs.get("user"),
            submitted_on=date.today(),
        )

        # pylint: disable=attribute-defined-outside-init
        self.package = package

        package.save()

    def before_save_instance(self, instance, row, **kwargs):  # pylint: disable=unused-argument, duplicate-code
        """Set the package and created_at fields for the imported samples."""
        instance.package = self.package
        instance.origin = "Admin"


class SampleAdmin(ImportExportModelAdmin):
    """Sequencing data hash admin page."""

    resource_classes = [SampleResource]

    read_only_fields = ["get_biosample_link"]

    list_display = [
        "id",
        "get_biosample_link",
        "submission_date",
        # "country",
        # "get_alias_biosample",
        # "get_alias_sequencing_biosample",
        # "get_other_aliases",
        # "get_scientific_species_name",
        "bioanalysis_status",
        "origin",
    ]

    raw_id_fields = [
        "ncbi_taxon",
    ]

    search_fields = ["aliases__name", "=id", "=biosample_id"]

    list_filter = [
        "country",
        "bioanalysis_status",
        "origin",
    ]

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Customize the form for the Sample model.

        The widget is set to a width of 250 pixels.
        """
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["biosample_id"].widget.attrs["style"] = "width: 250px"
        return form

    inlines = [
        SampleAliasInline,
        PhenotypicDrugSusceptibilityTestInline,
        MinimumInhibitoryConcentrationValueInline,
    ]

    def get_deleted_objects(self, objs, request):
        """Override to include aliases and sequencing data in deletion."""
        (
            deleted_objects,
            model_count,
            perms_needed,
            protected,
        ) = super().get_deleted_objects(objs, request)
        for obj in objs:
            deleted_objects.extend(
                [str(x) for x in obj.sequencing_data_set.filter(sample=obj)],
            )
            deleted_objects.extend([str(x) for x in obj.aliases.filter(sample=obj)])
            model_count["Sample aliass"] = (
                model_count.get("Sample aliass", 0)
                + obj.aliases.filter(sample=obj).count()
            )
            model_count["Sequencing data"] = (
                model_count.get("Sequencing data", 0)
                + obj.sequencing_data_set.filter(sample=obj).count()
            )

        return deleted_objects, model_count, perms_needed, protected

    def delete_model(self, request, obj):
        """Cascading deletion on sequencing data+alias."""
        obj.sequencing_data_set.filter(sample=obj).delete()
        obj.aliases.filter(sample=obj).delete()
        super().delete_model(request, obj)


admin.site.register(Sample, SampleAdmin)
