from django.core.management.base import BaseCommand
import pandas as pd
from Application.models import GeneralInfo
# from Application.models import OrthoInfy

class Command(BaseCommand):
    help= 'import booms'

    def handle(self, *args, **options):
#        Database connections
        df = pd.read_csv("Input_for_database_GeneralInfo.txt", sep="\t")
        for LncRNA_Id, LncRNA_Id1, Chr, Start, End, Strand, TSS, Promoter_start, Promoter_end, Length, Exon_number, Class, Direction, Location, Status_of_Expression, Orthologs_status, Overlap_gene_id, Overlap_ref_id, Class_code, Organism, Orthologs_Human, Orthologs_Chimp, Orthologs_Gorilla, Orthologs_Gibbon, DEGRegion_human, DEGRegion_chimp  in zip(df.LncRNA_Id, df.LncRNA_Id1, df.Chr, df.Start, df.End, df.Strand, df.TSS, df.Promoter_start, df.Promoter_end, df.Length, df.Exon_number, df.Class, df.Direction, df.Location, df.Status_of_Expression, df.Orthologs_status, df.Overlap_gene_id, df.Overlap_ref_id, df.Class_code, df.Organism, df.Orthologs_Human, df.Orthologs_Chimp, df.Orthologs_Gorilla, df.Orthologs_Gibbon, df.DEGRegion_human, df.DEGRegion_chimp ):
            models=GeneralInfo( LncRNA_id = LncRNA_Id,LncRNA_uid = LncRNA_Id1,Chr = Chr,Start = Start,End = End,Strand = Strand,TSS = TSS,Promoter_start = Promoter_start,Promoter_end = Promoter_end,Length = Length,Exon_number = Exon_number,Tr_Class = Class,Tr_Direction = Direction,Tr_Location = Location,Expression_status = Status_of_Expression,Orthologs_status = Orthologs_status,Overlap_gene_id = Overlap_gene_id,Overlap_ref_id = Overlap_ref_id,Class_code = Class_code,Organism = Organism, Orthologs_Human = Orthologs_Human, Orthologs_Chimp = Orthologs_Chimp, Orthologs_Gorilla = Orthologs_Gorilla, Orthologs_Gibbon = Orthologs_Gibbon, DEG_Human = DEGRegion_human, DEG_Chimp = DEGRegion_chimp  )
            models.save()

        # df1 = pd.read_csv("Input_for_database_Orthologs_table1.txt", sep="\t")
        # for Ortho_No, Organism1,LncRNA1,LncRNA_Id1,Organism2,LncRNA2 in zip(df1.Ortho_No, df1.Organism1, df1.LncRNA1, df1.LncRNA_Id1, df1.Organism2, df1.LncRNA2):
        #     models= OrthoInfy( OrthoNo=Ortho_No, Organism1= Organism1, Org_lncRNA1 = LncRNA1, LncRNA_uid_id = LncRNA_Id1, Organism2 = Organism2, Org_lncRNA2 = LncRNA2 )
        #     models.save()



