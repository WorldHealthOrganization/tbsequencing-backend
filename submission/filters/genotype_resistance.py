from django.db.models import Max
from django.db.models.functions import Coalesce
from django_filters import rest_framework as filters

from ..models import GenotypeResistance


class GenotypeResistanceFilter(filters.FilterSet):
    """GenotypeResistance filter."""

    sample_aliases_name = filters.CharFilter(
        field_name="sample__aliases__name",
        lookup_expr="icontains",
        distinct=True,
    )
    drug = filters.BaseInFilter(field_name="drug", lookup_expr="in")
    variant = filters.CharFilter(lookup_expr="icontains")

    @property
    def qs(self):
        """Apply default filtering by the latest variant version if no version filter is applied."""
        parent_queryset = super().qs

        if not self.request:
            return parent_queryset

        if not self.request.GET.get("version"):  # Check if "version" is not in the request
            latest_version = parent_queryset.aggregate(Max("version"))[
                "version__max"
            ]  # Find max version
            if latest_version is not None:
                # Filter for the latest version or null versions using COALESCE
                parent_queryset = parent_queryset.annotate(
                    coalesced_version=Coalesce("version", latest_version),
                ).filter(coalesced_version=latest_version)

        return parent_queryset

    class Meta:
        """Meta class."""

        model = GenotypeResistance
        fields = (
            "sample",
            "drug",
            "variant",
        )
