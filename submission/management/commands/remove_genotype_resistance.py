from django.core.management.base import BaseCommand
from django.db import connection

from submission.models import GenotypeResistance, Sample, SampleAlias

BATCH_SIZE = 10000


class Command(BaseCommand):
    """Remove test data from the database."""

    help = "Remove test data from the database"

    def delete_in_batches(self, model, filter_kwargs):
        """Delete records in batches using raw SQL for better performance."""
        # pylint: disable=W0212  # Accessing _meta is a common Django pattern for DB operations
        table_name = model._meta.db_table
        where_clause = " AND ".join([f"{k} LIKE '{v}%'" for k, v in filter_kwargs.items()])

        with connection.cursor() as cursor:
            # Get total count first
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}")
            total = cursor.fetchone()[0]

            # Delete in chunks using DELETE with LIMIT
            deleted = 0
            while deleted < total:
                cursor.execute(
                    f"DELETE FROM {table_name} WHERE id IN "
                    f"(SELECT id FROM {table_name} WHERE {where_clause} LIMIT {BATCH_SIZE})",
                )
                deleted += cursor.rowcount
                self.stdout.write(f"Deleted {deleted}/{total} {model.__name__} records...")

        return deleted

    def handle(self, *args, **options):
        """Handle the command."""
        self.stdout.write("Starting deletion process...")

        genotype_count = self.delete_in_batches(GenotypeResistance, {"variant": "test"})
        alias_count = self.delete_in_batches(SampleAlias, {"name": "test"})
        sample_count = self.delete_in_batches(Sample, {"isolation_source": "test"})

        self.stdout.write(
            f"\nFinal count of removed records:\n"
            f"- {sample_count} test Samples\n"
            f"- {alias_count} test Sample Aliases\n"
            f"- {genotype_count} test Genotype Resistances",
        )
