from django.db import models

from .drug import Drug
from .growth_medium import GrowthMedium
from .pds_assessment_method import PDSAssessmentMethod


class PDSTestCategory(models.Model):
    """Classification of each test based on method/medium/concentration/drug."""

    objects: models.Manager

    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        related_name="pdst_categories",
    )

    concentration = models.FloatField(blank=True, null=True)

    medium = models.ForeignKey(
        GrowthMedium,
        models.DO_NOTHING,
        null=True,
        related_name="categories",
    )

    # restrict cascade deletion
    method = models.ForeignKey(
        PDSAssessmentMethod,
        models.DO_NOTHING,
        null=True,
        related_name="categories",
    )

    category = models.TextField(null=False)

    class Meta:
        """Meta options for PDSTestCategory."""

        verbose_name_plural = "PDS Test Categories"
