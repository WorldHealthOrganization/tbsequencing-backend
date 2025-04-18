# Generated by Django 4.1.8 on 2023-04-13 17:53

import django.contrib.postgres.fields.ranges
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DrugGene",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "gene_db_crossref",
                    models.IntegerField(blank=True, null=True, unique=True),
                ),
                ("drug", models.IntegerField(blank=True, null=True, unique=True)),
                ("gene_name", models.CharField(max_length=100)),
                ("drug_name", models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="Gene",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("gene_db_crossref", models.IntegerField(null=True)),
                ("ncbi_id", models.CharField(max_length=128, null=True)),
                ("start_pos", models.IntegerField(null=True)),
                ("end_pos", models.IntegerField(null=True)),
                ("strand", models.IntegerField(null=True)),
                ("gene_name", models.TextField(null=True)),
                ("locus_tag", models.TextField(null=True)),
                ("gene_description", models.TextField(null=True)),
                ("gene_type", models.TextField(null=True)),
                ("protein_length", models.IntegerField(null=True)),
            ],
            options={
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="GeneDrugStats",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("gene_name", models.CharField(max_length=100)),
                ("gene_db_crossref", models.IntegerField()),
                ("variant_id", models.BigIntegerField(db_index=True)),
                ("variant_name", models.CharField(max_length=1024)),
                ("start_pos", models.IntegerField(null=True)),
                ("end_pos", models.IntegerField(null=True)),
                ("nucleodic_ann_name", models.CharField(db_index=True, max_length=100)),
                ("proteic_ann_name", models.CharField(db_index=True, max_length=100)),
                (
                    "consequence",
                    models.CharField(
                        choices=[
                            ("UPSTREAM", "Upstream"),
                            ("SYNONYMOUS", "Synonymous"),
                            ("MISSENSE", "Missense"),
                        ],
                        max_length=50,
                    ),
                ),
                ("total_counts", models.IntegerField()),
                ("global_frequency", models.FloatField()),
                ("resistant_count", models.IntegerField()),
                ("susceptible_count", models.IntegerField()),
                ("intermediate_count", models.IntegerField()),
            ],
            options={
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="GlobalResistanceStats",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("total_samples", models.IntegerField()),
                ("mono_resistant", models.IntegerField()),
                ("poly_resistant", models.IntegerField()),
                ("multidrug_resistant", models.IntegerField()),
                ("extensive_drug_resistant", models.IntegerField()),
                ("rifampicin_resistant", models.IntegerField()),
            ],
            options={
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="SampleDrugResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sampling_date",
                    django.contrib.postgres.fields.ranges.DateRangeField(null=True),
                ),
                ("test_result", models.CharField(max_length=1)),
            ],
            options={
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="SampleDrugResultStats",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sampling_date",
                    django.contrib.postgres.fields.ranges.DateRangeField(null=True),
                ),
                (
                    "resistance_type",
                    models.CharField(
                        choices=[("Pheno", "Phenotypic"), ("Geno", "Genotypic")],
                        max_length=64,
                    ),
                ),
                ("susceptible", models.IntegerField()),
                ("resistant", models.IntegerField()),
                ("intermediate", models.IntegerField()),
            ],
            options={
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="GeneSearchHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateTimeField(auto_created=True, auto_now=True)),
                (
                    "gene_db_crossref_id",
                    models.IntegerField(blank=True, null=True, unique=True),
                ),
                ("counter", models.IntegerField(blank=True, null=True)),
            ],
            options={
                "verbose_name_plural": "Gene search histories",
            },
        ),
    ]
