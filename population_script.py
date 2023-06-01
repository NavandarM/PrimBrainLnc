import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','PrimeOrthoLnc.settings')

import django
django.setup()

from Application.models import GeneralInfo

GeneralInfo.objects.all().delete()
import pandas as pd
data = pd.read_csv('Input_for_database_GeneralInfo_sequenceupdated.txt', sep = "\t")

#print(data.dtypes)
#data[['Start', 'End', 'TSS', 'Promoter_start','Promoter_end','Length','Location']] = data[['Start', 'End', 'TSS', 'Promoter_start','Promoter_end','Length','Location']].astype(int)
#print(data.dtypes)
#print(data.iloc[0]['Start']) #To access perticular cell in dataframe

row_iter = data.iterrows()

objs = [

    GeneralInfo(
        
        LncRNA_id = row['LncRNA_Id'],
        LncRNA_uid = row['LncRNA_Id1'],
        Chr = row['Chr'],
        Start = row['Start'],
        End = row['End'],
        Strand = row['Strand'],
        TSS = row['TSS'],
        Promoter_start = row['Promoter_start'],
        Promoter_end = row['Promoter_end'],
        Length = row['Length'],
        Exon_number = row['Exon_number'],
        Tr_Class = row['Class'],
        Tr_Direction = row['Direction'],
        Tr_Location = row['Location'],
        Expression_status = row['Status_of_Expression'],
        Orthologs_status = row['Orthologs_status'],
        Overlap_gene_id = row['Overlap_gene_id'],
        Overlap_ref_id = row['Overlap_ref_id'],
        Class_code = row['Class_code'],
        Organism = row['Organism'],
        Orthologs_Human = row['Orthologs_Human'],
        Orthologs_Chimp = row['Orthologs_Chimp'],
        Orthologs_Gorilla = row['Orthologs_Gorilla'],
        Orthologs_Gibbon = row['Orthologs_Gibbon'],
        DEG_Human = row['DEGRegion_human'],
        DEG_Chimp = row['DEGRegion_chimp'],
        Sequence = row['Sequence'],

    )
    for index, row in row_iter
]

GeneralInfo.objects.bulk_create(objs)