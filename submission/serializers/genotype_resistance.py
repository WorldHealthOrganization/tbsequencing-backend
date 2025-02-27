from rest_framework import serializers


class GenotypeResistanceSerializer(serializers.Serializer):  # pylint: disable=W0223
    """Genotype Resistance info retrieving serializer."""

    drug_name = serializers.CharField(source="drug.drug_name")
    sample_aliases_name = serializers.SerializerMethodField()
    variant = serializers.CharField(read_only=True)
    resistance_flag = serializers.CharField(read_only=True)

    def get_sample_aliases_name(self, obj):
        """Get the name of the first alias of the sample."""
        if hasattr(obj.sample, "filtered_aliases") and obj.sample.filtered_aliases:
            return obj.sample.filtered_aliases[0].name
        return None
