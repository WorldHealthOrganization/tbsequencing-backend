from django.db import models


class GenotypeResistance(models.Model):
    """Predicted (genotypical) resistance data."""

    objects: models.Manager

    sample = models.ForeignKey(
        "Sample",
        on_delete=models.CASCADE,
        related_name="genotype_resistances",
    )
    drug = models.ForeignKey(
        "genphen.Drug",
        on_delete=models.CASCADE,
        related_name="genotype_resistances",
    )
    variant = models.CharField(max_length=32 * 1024)

    version = models.IntegerField(default=1, db_index=True)

    resistance_flag = models.CharField(max_length=10)

    class Meta:
        """Meta class."""

        indexes = [
            models.Index(fields=["sample", "drug"]),
            models.Index(fields=["version", "drug_id"], name="idx_version_drug_id"),
        ]
