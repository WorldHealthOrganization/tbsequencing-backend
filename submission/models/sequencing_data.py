from typing import Any

from django.db import models
from django.db.models.functions import Upper
from django.utils.html import format_html

from submission.util.storage import FastqPermanentStorage

from .package import Package
from .sample import Sample


class SequencingData(models.Model):
    """
    Sequencing Data model.

    Stores sequencing data files info, submitted both from the application and NCBI.
    The files themselves stored at S3 bucket.
    """

    objects: models.Manager

    class Meta:
        """Sequencing data model options."""

        verbose_name_plural = "Sequencing data"

        constraints = [
            models.UniqueConstraint(
                "library_name",
                "file_path",
                name="uc__sequencing_data__library_name__file_path",
            ),
        ]
        indexes = [
            # for iexact to work fast
            models.Index(
                Upper("library_name"),
                name="sd__library_name__upper__idx",
            ),
        ]

    class DataLocation(models.TextChoices):
        """Possible data location enum."""

        NCBI = "NCBI"
        TBKB = "TB-Kb"
        CNCB = "CNCB"

    class StorageClass(models.TextChoices):
        """Possible S3 storage classes."""

        STANDARD = "STANDARD"
        DEEP_ARCHIVE = "DEEP_ARCHIVE"
        EMPTY = ""

    # app-defined column, used to distinguish original file @ matching stage
    created_at = models.DateTimeField(auto_now_add=True)

    # app-defined, filename of file on S3.
    # Defined as FileField
    # in order to get correct download link in admin section
    filename = models.FileField(storage=FastqPermanentStorage(), null=True, blank=True)
    # app-defined, file size in bytes
    file_size = models.BigIntegerField(null=True)

    # library_name could be a Sample name, should be used to match Fastq with Sample
    library_name = models.CharField(max_length=8_192, blank=True)

    # S3 path (without bucket)
    file_path = models.CharField(max_length=8_192, null=True, unique=True)

    # data origin (NCBI, TB-Kb (new), ...)
    data_location = models.CharField(max_length=8_192, choices=DataLocation.choices)

    # Storage class of the file at S3.
    s3_storage_class = models.CharField(
        max_length=50,
        null=True,
        choices=StorageClass.choices,
        default=StorageClass.STANDARD,
    )

    # not used by app
    library_preparation_strategy = models.CharField(max_length=8_192, null=True, blank=True)
    dna_source = models.CharField(max_length=8_192, null=True, blank=True)
    dna_selection = models.CharField(max_length=8_192, null=True, blank=True)
    sequencing_platform = models.CharField(max_length=8_192, null=True, blank=True)
    sequencing_machine = models.CharField(max_length=8_192, null=True, blank=True)
    library_layout = models.CharField(max_length=8_192, null=True, blank=True)
    assay = models.CharField(max_length=8_192, null=True, blank=True)

    # FK's
    sample = models.ForeignKey(
        Sample,
        on_delete=models.SET_NULL,  # leave even if sample is deleted
        null=True,  # changed to nullable, so we can link sample later, at matching stage
        related_name="sequencing_data_set",
    )
    # M2M link, in order to track where the object is used
    packages = models.ManyToManyField(
        Package,
        through="PackageSequencingData",
        related_name="sequencing_datas",
    )
    assoc_packages: Any  # RelatedManager[PackageSequencingData]
    hashes: Any  # RelatedManager[SequencingDataHash]

    def __str__(self):
        """Represent instance for admin site."""
        return f"Sequencing data #{self.pk} {self.data_location or ''}"

    def get_filenames(self):
        """Output all filename that were ever associated with this file."""
        return ", ".join([s.filename for s in self.assoc_packages.all()])

    def get_library_url(self):
        """Aggregate aliases to display in the admin panel."""
        if not self.library_name:
            return ()
        return format_html(
            '<a href="{0}">{1}</a>',
            "https://www.ncbi.nlm.nih.gov/sra/" + str(self.library_name),
            self.library_name,
        )

    get_library_url.short_description = "Library name"
    get_filenames.short_description = "File name"
