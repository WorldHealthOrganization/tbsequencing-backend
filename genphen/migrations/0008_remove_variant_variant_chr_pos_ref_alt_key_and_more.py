# Generated by Django 4.1.5 on 2023-05-24 18:22

from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):

    dependencies = [
        ("genphen", "0007_initial_data"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="variant",
            name="variant_chr_pos_ref_alt_key",
        ),
        migrations.AddConstraint(
            model_name="variant",
            constraint=models.UniqueConstraint(
                models.F("chromosome"),
                models.F("position"),
                django.db.models.functions.text.MD5("reference_nucleotide"),
                django.db.models.functions.text.MD5("alternative_nucleotide"),
                name="variant_chr_pos_ref_alt_uniq",
            ),
        ),
    ]
