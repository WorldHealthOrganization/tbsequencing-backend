from django.contrib import admin, messages
from django.db.models import Count, Case, When, Value, IntegerField, Q
from django.utils.html import format_html

from fsm_admin2.admin import FSMTransitionMixin

from submission.models import Package, Sample
from .attachment import AttachmentInline
from .communication import MessageInline
from .package_stats import PackageStatsInline
from .package_sequencing_data_inline import PackageSequencingDataInline
from .contributor import ContributorInline


class PackageOriginListFilter(admin.SimpleListFilter):
    """Custom admin filter, showing packages by their origin."""

    title = "package origin"
    parameter_name = "origin"

    def lookups(self, request, model_admin):
        """Available filter options."""
        return (
            (None, "TbKb"),
            ("ncbi", "NCBI"),
            ("all", "All"),
            ("admin", "Admin"),
        )

    def choices(self, changelist):
        """Highlight selected choice."""
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == lookup,
                "query_string": changelist.get_query_string(
                    {
                        self.parameter_name: lookup,
                    },
                    [],
                ),
                "display": title,
            }

    def queryset(self, request, queryset):
        """Filter by selected choice."""
        if self.value() == "ncbi":  # `ncbi`
            return queryset.filter(
                owner__isnull=True,
            )
        if not self.value():  # `tbkb`
            return queryset.filter(
                owner__isnull=False,
            )
        if self.value() == "admin":
            return queryset.filter(
                origin="Admin"
            )
        return queryset  # `all` and anything else


@admin.register(Package)
class PackageAdmin(FSMTransitionMixin, admin.ModelAdmin):
    """Package admin page."""

    fsm_fields = [
        "state",
    ]

    list_display = (
        "name", 
        "get_bioproject_link",
        "owner",
        "samples_count",
        "samples_with_pdst_from_any_packages",
        "state_ordered",
        "state_changed_on",
    )

    inlines = [
        PackageStatsInline,
        AttachmentInline,
        PackageSequencingDataInline,
        MessageInline,
        ContributorInline
    ]

    readonly_fields = (
        "bioproject_id",
        "state_changed_on",
        "owner",
        "name",
        "description",
        "matching_state",
        "samples_count",
        "samples_left_for_processing",
        "unmatched_samples_count",
        "unmatched_mic_tests_count",
        "unmatched_pds_tests_count",
        "rejection_reason",
        "samples_with_pdst_from_any_packages",
        "get_bioproject_link"
    )

    actions = [
        "schedule_samples"
    ]

    ordering = ["-state_changed_on"]
    # actions = [accept_pending_package, reject_pending_package]
    list_filter = [
        "state",
        PackageOriginListFilter,
        ("owner", admin.RelatedOnlyFieldListFilter),
    ]

    search_fields = [
        "name"
    ]

    actions = [
        "schedule_samples"
    ]



    def get_queryset(self, request):
        """Annotate queryset with additional data."""
        query = super().get_queryset(request)
        # samples count is being showed at package list, so we want to pre-calculate it
        query = query.annotate(samples_count=Count("sample_aliases__sample", distinct=True))
        query = query.annotate(
            state_ordered=Case(
                When(state=Package.State.PENDING, then=Value(1)),
                When(state=Package.State.DRAFT, then=Value(2)),
                When(state=Package.State.REJECTED, then=Value(3)),
                When(state=Package.State.ACCEPTED, then=Value(4)),
                output_field=IntegerField(),
            ),
        )

        return query

    @admin.action(description="Schedule associated samples for bionformatic analysis.")
    def schedule_samples(self, request, queryset):
        count = 0
        for obj in queryset:
            selection = (
                obj
                .sample_aliases
                .filter(
                    Q(sample__bioanalysis_status__isnull=True)
                    & Q(sample__ncbi_taxon_id=1773)
                )
                .values_list("sample")
                .distinct()
                .all()
            )

            count+=len(selection)

            Sample.objects.filter(pk__in=selection).update(
                bioanalysis_status="Unprocessed"
            )
            
        self.message_user(
            request,
            f"{count} samples were scheduled for analysis.",
            messages.SUCCESS,
        )
        return

    @admin.display(description="BioProject ID")
    def get_bioproject_link(self, obj):
        """Get biosample link"""
        if not obj.bioproject_id or obj.bioproject_id<0:
            return ""
        return(format_html(
            '<a href="{0}">{1}</a>',
            "https://www.ncbi.nlm.nih.gov/bioproject/"+str(obj.bioproject_id),
            obj.bioproject_id
            )
        )

    @admin.display(ordering="samples_count")
    def samples_count(self, obj):
        """
        Show sample aliases count for a package.

        Only counter that is being annotated into queryset,
        because it's being shown at package list.
        Other counters are shown on package details page,
        so they produce separate sql request each,
        making it easier for DB to handle.
        """
        return obj.samples_count


    @admin.action(description="Schedule associated samples for bionformatic analysis.")
    def schedule_samples(self, request, queryset):
        count = 0
        for obj in queryset:
            selection = (
                obj
                .sample_aliases
                .filter(
                    Q(sample__bioanalysis_status__isnull=True)
                    & Q(sample__ncbi_taxon_id=1773)
                )
                .values_list("sample")
                .distinct()
                .all()
            )

            print(selection, len(selection))
            count+=len(selection)

            Sample.objects.filter(pk__in=selection).update(
                bioanalysis_status="Unprocessed"
            )

        self.message_user(
            request,
            f"{count} samples were scheduled for analysis.",
            messages.SUCCESS,
        )
        return
    
    @admin.display()
    def samples_left_for_processing(self, obj):
        """Show number of samples that have been through the bioinformatic pipeline."""
        return (
            obj.sample_aliases
            .filter(
                Q(sample__bioanalysis_status__isnull=True)
            )
            .values("sample")
            .distinct()
            .count()
        )

    @admin.display()
    def unmatched_samples_count(self, obj):
        """Show unmatched sample aliases count for a package."""
        return obj.sample_aliases.filter(sample__isnull=True).count()

    @admin.display()
    def unmatched_mic_tests_count(self, obj):
        """Show unmatched MIC tests count for a package."""
        return obj.mic_tests.filter(sample__isnull=True).count()

    @admin.display()
    def unmatched_pds_tests_count(self, obj):
        """Show unmatched PDS tests count for a package."""
        return obj.pds_tests.filter(sample__isnull=True).count()

    @admin.display(description="Samples with unstaged pDST/MIC.")
    def samples_with_pdst_from_any_packages(self, obj):
        """Show the number of samples with test that are not staged."""
        return(
            obj.sample_aliases.filter(
                (
                    Q(sample__pds_tests__test_result__isnull=False)
                    & ~Q(sample__pds_tests__staging="t")
                )
                |
                (
                    Q(sample__mic_tests__range__isnull=False)
                    & ~Q(sample__mic_tests__staging="t")
                )
            )
            .values("sample")
            .distinct()
            .count()
        )


    @admin.display(ordering="state_ordered", description="State")
    def state_ordered(self, obj):
        """Show package state, ordered naturally."""
        return obj.state

    @admin.display(ordering="owner__email")
    def owner_email(self, obj):
        """
        Show package owner email.

        Some system-purposed packages could have no owner,
        so we check it there.
        """
        if obj.owner:
            return obj.owner.email
        return None

    @admin.display()
    def get_actions(self, request):
        """Remove "delete selected packages" from admin actions."""
        actions = super().get_actions(request)
        del actions["delete_selected"]
        return actions

    @admin.display()
    def samples_left_for_processing(self, obj):
        """Show number of samples that have not been through the bioinformatic pipeline."""
        return (
            obj.sample_aliases
            .filter(
                Q(sample__bioanalysis_status__isnull=True)
                & Q(sample__ncbi_taxon_id=1773)

            )
            .values("sample")
            .distinct()
            .count()
        )
