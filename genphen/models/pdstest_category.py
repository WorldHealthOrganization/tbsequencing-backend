from django.db import models
from . import Drug, GrowthMedium, PDSAssessmentMethod

class PDSTestCategory(models.Model):
    """Classification of each test based on method/medium/concentration/drug"""

    objects: models.Manager

    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        related_name="pdst_categories",
    )

    concentration = models.FloatField(
        blank=True,
        null=True
    )

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

    category = models.TextField(
        null=False
    )


    class Meta:
        verbose_name_plural = "PDS Test Categories"
