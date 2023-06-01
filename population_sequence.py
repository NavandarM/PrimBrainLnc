import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','PrimeOrthoLnc.settings')

import django
django.setup()

from Application.models import GeneralInfo, Sequence_table

import pandas as pd

GeneralInfo.objects.all().delete()
Sequence_table.objects.all().delete()

general_info_df = pd.read_csv('Input_for_database_GeneralInfo.txt', sep = "\t")

# Iterate over the rows of the DataFrame
for _, row in general_info_df.iterrows():
    general_info = GeneralInfo(
        LncRNA_id=row['LncRNA_Id'],
        LncRNA_uid=row['LncRNA_Id1'],
        Chr=row['Chr'],
        Start=row['Start'],
        End=row['End'],
        Strand=row['Strand'],
        TSS=row['TSS'],
        Promoter_start=row['Promoter_start'],
        Promoter_end=row['Promoter_end'],
        Length=row['Length'],
        Exon_number=row['Exon_number'],
        Tr_Class=row['Class'],
        Tr_Direction=row['Direction'],
        Tr_Location=row['Location'],
        Expression_status=row['Status_of_Expression'],
        Orthologs_status=row['Orthologs_status'],
        Overlap_gene_id=row['Overlap_gene_id'],
        Overlap_ref_id=row['Overlap_ref_id'],
        Class_code=row['Class_code'],
        Organism=row['Organism']
    )
    general_info.save()


# Sequence population
sequence_table_df = pd.read_csv('Input_for_sequence_table.txt', sep='\t')

#Iterate over the rows of the DataFrame
for _, row in sequence_table_df.iterrows():
    # Retrieve the related GeneralInfo instance using LncRNA_uid
    general_info = GeneralInfo.objects.get(LncRNA_uid=row['LncRNA_Id1'])

    sequence_table = Sequence_table(
        LncRNA_uid=general_info,
        Sequence=row['sequence']
    )
    sequence_table.save()