import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max

from biosql.models import Taxon
from genphen.models import Drug
from submission.models import GenotypeResistance, Package, Sample, SampleAlias

BATCH_SIZE = 1000


class Command(BaseCommand):
    """Generate genotype resistance data."""

    help = "Generate genotype resistance data"

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument("num_objects", type=int, help="Number of objects to generate")

    def handle(self, *args, **options):
        """Handle the command."""
        num_objects = options["num_objects"]
        self.generate_genotype_resistance(num_objects)

    def generate_genotype_resistance(self, num_objects):
        """Generate genotype resistance data."""
        # Ensure Taxon exists
        taxon, _ = Taxon.objects.get_or_create(taxon_id=1, defaults={"node_rank": "species"})

        # Ensure Drugs exist
        drugs = list(Drug.objects.filter(pk__in=range(1, 26)))
        if not drugs:
            for i in range(1, 26):
                drug = Drug(drug_id=i, drug_name=f"testDrug{i}", drug_code=f"D{i}")
                drug.save()
            drugs = list(Drug.objects.filter(pk__in=range(1, 26)))

        # Ensure Package exists
        package, _ = Package.objects.get_or_create(
            pk=1,
            defaults={"name": "test Default Package", "description": "Generated package"},
        )

        samples = []
        sample_aliases = []
        genotype_resistances = []

        max_version = GenotypeResistance.objects.aggregate(Max("version"))["version__max"] or 1

        for i in range(num_objects):
            sample = Sample(
                origin=Sample.Origin.NCBI,
                ncbi_taxon=taxon,
                isolation_source="test",
            )
            samples.append(sample)

            sample_alias = SampleAlias(
                sample=sample,
                origin=SampleAlias.Origin.BIOSAMPLE,
                origin_label=Sample.SAMPLE_NAME,
                name="test" + "".join(random.choices("0123456789ABCDEF", k=15)),
                package=package,
            )
            sample_aliases.append(sample_alias)

            genotype_resistance = GenotypeResistance(
                sample=sample,
                drug=random.choice(drugs),
                variant="test" + "".join(random.choices("0123456789ABCDEF", k=15)),
                resistance_flag=random.choice(["S", "R", "I"]),
                version=max_version,
            )
            genotype_resistances.append(genotype_resistance)

            if (i + 1) % BATCH_SIZE == 0:
                with transaction.atomic():
                    Sample.objects.bulk_create(samples)
                    SampleAlias.objects.bulk_create(sample_aliases)
                    GenotypeResistance.objects.bulk_create(genotype_resistances)
                samples.clear()
                sample_aliases.clear()
                genotype_resistances.clear()

        # Insert any remaining objects
        if samples:
            with transaction.atomic():
                Sample.objects.bulk_create(samples)
                SampleAlias.objects.bulk_create(sample_aliases)
                GenotypeResistance.objects.bulk_create(genotype_resistances)

        self.stdout.write(
            f"\nFinal count of generated records:\n"
            f"- {num_objects} Samples\n"
            f"- {num_objects} Sample Aliases\n"
            f"- {num_objects} Genotype Resistances",
        )
