from django.db import models


class VariantAdditionalInfo(models.Model):
    """Variant grades model."""

    objects: models.Manager

    position = models.IntegerField(null=True)

    alternative_nucleotide = models.CharField(null=True, max_length=200)

    reference_nucleotide = models.CharField(null=True, max_length=200)

    variant = models.ForeignKey(
        "Variant",
        on_delete=models.CASCADE,
        related_name="v1_annotations",
        null=True,
    )

    v1_annotation = models.TextField()
