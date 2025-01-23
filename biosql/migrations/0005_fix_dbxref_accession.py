# Manually written

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('biosql', '0004_fix_alr_gene'),
    ]

    ncbi_wrong_prot_alr_id = 'NP_217940.1'
    uniprot_correct_prot_alr_id = 'P9WQA9'

    operations = [
            migrations.RunSQL(
                sql = [("""
                UPDATE dbxref.accession
                    SET
                        value = %s
                    WHERE
                        value = %s;
                """, [uniprot_correct_prot_alr_id, ncbi_wrong_prot_alr_id]
                )],
                reverse_sql=[("""            
                UPDATE dbxref.accession
                    SET
                        value = %s
                    WHERE
                        value = %s;
                """, [ncbi_wrong_prot_alr_id, uniprot_correct_prot_alr_id]
                )]
            ),
    ]
