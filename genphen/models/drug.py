from typing import Any

from django.db import models


class Drug(models.Model):
    """Drug non-managed model."""

    objects: models.Manager

    drug_id = models.AutoField(primary_key=True)
    drug_name = models.CharField(max_length=8_192, unique=True)
    # preferred drug code
    drug_code = models.CharField(max_length=8_192, unique=True)

    synonyms: Any  # RelatedManager[DrugSynonym]
    mic_tests: Any  # RelatedManager[MICTest]
    pds_tests: Any  # RelatedManager[PDSTest]
    gene_resistance_associations: Any  # RelatedManager[GeneDrugResistanceAssociation]
    variant_grades: Any  # RelatedManager[VariantGrade]

    def __str__(self):
        """Human readable representation."""
        return f"{self.drug_id} - {self.drug_name}"
