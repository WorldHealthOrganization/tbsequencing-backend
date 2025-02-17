# Generated by Django 4.1.5 on 2023-04-21 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0002_alter_samplealias_match_source_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="samplealias",
            name="match_source",
            field=models.CharField(
                choices=[
                    ("NO_MATCH", "No match found"),
                    ("FASTQ_UPLOADED", "Uploaded FASTQ file"),
                    ("FASTQ_UPLOADED_NEW_SAMPLE", "Uploaded FASTQ file, new sample"),
                    ("FASTQ_EXISTING", "Existing FASTQ file"),
                    ("NCBI", "NCBI sample name"),
                    ("NCBI_FASTQ", "Existing FASTQ file at NCBI"),
                    ("USER_ALIAS", "Existing user alias"),
                ],
                max_length=64,
                null=True,
            ),
        ),
    ]
