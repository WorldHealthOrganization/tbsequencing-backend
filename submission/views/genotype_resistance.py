from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from common.paginations import PluggablePageSizePageNumberPagination

from ..filters import GenotypeResistanceFilter
from ..models import GenotypeResistance, Sample, SampleAlias
from ..serializers import GenotypeResistanceSerializer


class GenotypeResistanceViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):
    """Genotype Resistance data (table at the bottom of Genotype Resistance tabs)."""

    serializer_class = GenotypeResistanceSerializer
    pagination_class = PluggablePageSizePageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GenotypeResistanceFilter

    def get_queryset(self):
        """Get queryset."""
        sample_alias_prefetch = Prefetch(
            "sample__aliases",
            queryset=SampleAlias.objects.filter(origin=SampleAlias.Origin.BIOSAMPLE).order_by("id"),
            to_attr="filtered_aliases",
        )

        queryset = (
            GenotypeResistance.objects.filter(
                sample__origin=Sample.Origin.NCBI,
            )
            .select_related("drug", "sample")
            .prefetch_related(sample_alias_prefetch)
            .order_by("id")
            .only(
                "id",
                "sample_id",
                "drug_id",
                "variant",
                "resistance_flag",
            )
        )

        return queryset
