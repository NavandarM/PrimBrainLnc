from Application.models import GeneralInfo

DEFAULT_FIELDS = dict(
    Chr='chr1', Start=1000, End=2000, Strand='+', TSS='1000',
    Promoter_start='900', Promoter_end='1000', Length='1000', Exon_number='2',
    Tr_Class='lincRNA', Tr_Direction='sense', Tr_Location='intergenic',
    Expression_status='Expressed', Orthologs_status='1:1',
    Overlap_gene_id='', Overlap_ref_id='', Class_code='u',
    DEG_Human='', DEG_Chimp='', Sequence='ATCGATCGATCG',
    # Orthologs default to the literal string "nan": templates check `!= "nan"` before
    # rendering a link, and the str path converter rejects an empty segment outright.
    Orthologs_Human='nan', Orthologs_Chimp='nan', Orthologs_Gorilla='nan', Orthologs_Gibbon='nan',
)


def make_general_info(lncrna_id, organism, **overrides):
    fields = dict(DEFAULT_FIELDS)
    fields.update(
        LncRNA_id=lncrna_id,
        LncRNA_uid=f'{lncrna_id}_{organism}',
        Organism=organism,
    )
    fields.update(overrides)
    return GeneralInfo.objects.create(**fields)
