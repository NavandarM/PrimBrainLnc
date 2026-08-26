from django.shortcuts import render
from Application.models import GeneralInfo
from .forms import ExplorationFormByIDs, UserMessageForm, ExplorationForm, ExploreFormSeq, ExploreMultipleIds
from django.http import HttpResponseRedirect
from django.contrib import messages
import re
from functools import lru_cache
from django.views.generic import TemplateView
import pandas as pd
import numpy as np
import os
from django.conf import settings
import subprocess
from django.urls import reverse
from django.utils.safestring import mark_safe
from html import unescape
import plotly.express as px

# Organism name -> UCSC genome browser assembly id, shared by every search path
ORGANISM_ASSEMBLY = {"Human": "hg19", "Chimp": "panTro4", "Gorilla": "gorGor4", "Gibbon": "nomLeu3"}


# View: Home Page
class  IndexView(TemplateView):
    template_name = "index.html"
    def get_context_data(self, **kwargs):
        HomePageContent = super().get_context_data(**kwargs)
        HomePageContent['insert_content'] = 'Welcome to PrimBrainLnc'
        return HomePageContent

# View: Search Page
def search(request):
    Queries = GeneralInfo.objects.all()
    return render(request, 'search.html', {'Total_Entries':Queries})

# View: Statistics
def statistics(request):
    return render(request, 'statistics.html')

# View: Downloads
def downloads(request):
    return render(request, 'downloads.html')

# View: Contact
def contact(request):
    return render(request,'contact.html')

# View: Frequently Asked Questions
def faqs(request):
    return render(request, 'faqs.html')

# View: User Feedback
def userArea(request):
    submitted = False
    if request.method == 'POST':
        form= UserMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/ApplicationuserArea?submitted=True')
    else:
        form= UserMessageForm
        if 'submitted' in request.GET:
            submitted= True
    return render(request, 'user_input.html',{'form':form, 'submitted':submitted})

#### Function of splitting the string into a specific pattern
def query_processor(query_entity, organism_entity):

    entry = query_entity.first()
    if entry is None:
        return f"No entires found! Probably you entered invalid lncRNA id for {organism_entity}"

    orthologs = [
        getattr(entry, field).replace(' ', '').split(';')
        for field in ('Orthologs_Human', 'Orthologs_Chimp', 'Orthologs_Gorilla', 'Orthologs_Gibbon')
    ]
    return orthologs + [entry.LncRNA_id]

#### Preparation of the data for visualization

REGION_ORDER = ['CB', 'STR', 'HIP', 'ACC', 'DPFC', 'VPFC', 'PMC', 'V1C']  # display order for the boxplot
EXPRESSION_FILES = {
    'Human': 'Normalized_Read_Counts_Human.txt',
    'Chimp': 'Normalized_Read_Counts_Chimp.txt',
    'Gorilla': 'Normalized_Read_Counts_Gorilla.txt',
}


@lru_cache(maxsize=None)
def _load_expression_data(organism):
    # These files are multi-MB; parse each one once per process instead of on every request.
    file_path = os.path.join(settings.STATIC_DIR, 'files/ExpressionCounts', EXPRESSION_FILES[organism])
    return pd.read_csv(file_path, sep="\t").set_index('Ids')


def Data_preparation(organism, lncRNA_Id):
    if organism not in EXPRESSION_FILES:
        return "Expression is Not available!"

    try:
        Exp_data1 = _load_expression_data(organism)
        Entity = Exp_data1.loc[lncRNA_Id].to_frame()                    # Accessing the records of the given lncRNA_Id
        Entity['Region'] = [re.sub(".*_.*.*_", "", name) for name in Entity.index]      # Get the name of region from the columns of the expression data
        Entity['Region'] = [re.sub(".bam.out", "", name) for name in Entity['Region'] ]
        Entity['Region'] = pd.Categorical(Entity['Region'], categories=REGION_ORDER, ordered=True)     # It will infer the categories and their order from the input data
        Entity['Log2_Expression'] = np.log2(Entity[lncRNA_Id] + 1)

        plot_title = 'Expression for ' + lncRNA_Id
        fig = px.box(Entity, x="Region", y="Log2_Expression", color="Region", category_orders={'Region': REGION_ORDER}, width=850, height=500)
        fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default
        export = fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5 ),
                                    title={'text': plot_title, 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                                    yaxis_title= "log2 (Expression)",
                                    xaxis_title= "Regions",
                                    legend_title="" )
        return export.to_html()
    except KeyError:
        return f"Expression is Not available for {lncRNA_Id}"

def Results_from_ids(request, lncIDs, OrgS ):

    ORG= OrgS.capitalize()
    Ids_query = GeneralInfo.objects.filter(LncRNA_id__iexact=lncIDs, Organism__iexact=ORG)
    ORG_Id= ORGANISM_ASSEMBLY[ORG]
    ortho = query_processor(Ids_query, ORG )
    Box_Plot = Data_preparation(organism=ORG, lncRNA_Id= lncIDs)
    if isinstance(ortho, list):
        return render(request, 'results.html', {'Ids_results':Ids_query, 'hsa_ortho':ortho[0], 'pan_ortho':ortho[1], 'gor_ortho':ortho[2], 'gib_ortho':ortho[3], 'graph': Box_Plot, 'browser_org':ORG_Id})
    else:
        return render(request, 'warnings.html',{'Warn':ortho})


PURE_LNC_FASTA = {
    'Human': 'Hsapiens_Pure_lncrnas.fasta',
    'Chimp': 'Chimp_pure_lncRNAs.fasta',
    'Gorilla': 'Gorilla_pure_lncRNAs.fasta',
    'Gibbon': 'Gibbon_pure_lncRNAs.fasta',
}


### Run the blast
def run_blast(input_file, database_name):
    ## fasta sequences from organisms to consider
    fasta_paths = [
        os.path.join(settings.STATIC_DIR, 'files/purelncs', PURE_LNC_FASTA[organism])
        for organism in PURE_LNC_FASTA
        if any(organism in db_entity for db_entity in database_name)
    ]

    # All the paths of the files
    Input_genome_pre= os.path.join(settings.STATIC_DIR,'Tmp','GenomePrepInput.fasta')
    with open(Input_genome_pre, 'w') as combined_fasta:
        for path in fasta_paths:
            with open(path) as fasta_file:
                combined_fasta.write(fasta_file.read())

    out_path_db=os.path.join(settings.STATIC_DIR,'Tmp','OrganismDB')

    # Build the customized BLAST database (makeblastdb/blastn come from the
    # conda-installed `blast` package, resolved via PATH)
    subprocess.run(['makeblastdb', '-in', Input_genome_pre, '-dbtype', 'nucl', '-title', 'organism', '-out', out_path_db], check=True)

    ## Preapration for Blast
    out_path=os.path.join(settings.STATIC_DIR,'Tmp','BLAST_output.txt')

    # Run standalone blastn
    subprocess.run([
        'blastn', '-query', input_file, '-db', out_path_db, '-out', out_path,
        '-evalue', '0.001', '-outfmt', '6', '-perc_identity', '95', '-max_target_seqs', '20',
    ], check=True)

    if is_file_not_empty(out_path):
        Blast_output = pd.read_csv(out_path,sep='\t', header=None)
        new_headers = ['Query', 'Hit_in_Database', 'Per identity', 'Alignment length', 'Mismatches', 'Gap opens', 'Qurey start', 'Qurey end', 'Hit start', 'Hit end', 'E-value', 'Bit score']
        Blast_output.columns = new_headers

        Blast_output_subset = Blast_output[['Query', 'Hit_in_Database', 'Per identity', 'Alignment length', 'Mismatches', 'Hit start', 'Hit end', 'E-value', 'Bit score']].copy()
        Blast_output_subset['Hit_in_Database'] = Blast_output_subset['Hit_in_Database'].apply(create_hyperlink)

        Blast_output_subset= Blast_output_subset.to_html(index=False, header=True, classes='table table-bordered', justify='center')

        Blast_output_subset = unescape(Blast_output_subset)  ## To get ride of &lt; AND &gt

        return mark_safe(Blast_output_subset)
    else:
        return('No hit for the given query!')

## To check if blast output file is empty
def is_file_not_empty(file_path):
    return os.path.getsize(file_path) > 0

## To give hyperlink to blast hits from database
def create_hyperlink(Hit_in_Database):
    lncRNA_Id, Organism = Hit_in_Database.rsplit('_', 1)
    url = reverse('Application:results-from-ids', args=(lncRNA_Id.strip(), Organism.strip()))
    #hyperlink = format_html('<a href="{}">{}</a>', url, Hit_in_Database)
    #return hyperlink
    
    url = reverse('Application:results-from-ids', args=(lncRNA_Id, Organism))
    return mark_safe(f'<a href="{url}">{Hit_in_Database}</a>')

## Process the input of the browse webpage.
def Explore(request):
    
    if request.method == 'POST':
        id_search_form = ExplorationFormByIDs(request.POST)
        Loc_search_form = ExplorationForm(request.POST)
        seq_search_form = ExploreFormSeq(request.POST)
        multipleID_search_form = ExploreMultipleIds(request.POST)

        ### IDs based search

        if id_search_form.is_valid() and request.POST.get('Idss'):
            IDS = request.POST.get("ID").strip()
            ORG = request.POST.get("Organism").capitalize().strip()
            ORG_Id= ORGANISM_ASSEMBLY[ORG]

            ## Query based on the input IDs AND extracting information.

            if IDS and ORG:
                Ids_query = GeneralInfo.objects.filter(LncRNA_id__iexact=IDS, Organism__iexact=ORG )
                ortho = query_processor(Ids_query, ORG )
                Box_Plot = Data_preparation(organism=ORG, lncRNA_Id= IDS)

                if isinstance(ortho, list):
                    return render(request, 'results.html', {'Ids_results':Ids_query, 'hsa_ortho':ortho[0], 'pan_ortho':ortho[1], 'gor_ortho':ortho[2], 'gib_ortho':ortho[3], 'graph': Box_Plot, 'browser_org':ORG_Id})
                else:
                    return render(request, 'warnings.html',{'Warn':ortho})
            else:
                messages.info(request, 'Please specify ID and Organism!')
                return HttpResponseRedirect('/ApplicationExplore/')
            
        ### Location based search

        if Loc_search_form.is_valid() and request.POST.get('Locations'):
            Position= request.POST.get("Location")
            ORG= request.POST.get("Organism").capitalize().strip()
            Overlap = request.POST.get("Overlap")
            if Position and ORG:
                Location_pattern= re.compile(r'(\S+):(\S+)-(\S+)')
                Location_group = Location_pattern.search(Position.replace(" ",""))
                q_CHR, q_START, q_END = Location_group.groups()
                
                ## To allow overlap if user interested, otherwise default is zero!:
                if Overlap:
                    if int(Overlap) > 0 or int(Overlap) < 0:
                        Overlap= int(Overlap)
                    else:
                        Overlap=0
                    q_START1 = int(q_START)- int(Overlap)
                    q_START2= int(q_START) + int(Overlap)
                    q_END1 = int(q_END) + int(Overlap)
                else:
                    q_START1 = int(q_START)
                    q_START2= int(q_START)
                    q_END1 = int(q_END)

                ORG_Id= ORGANISM_ASSEMBLY[ORG]

                ## Query based on the input co-ordinates + overlap if any AND extracting information.
                Location_query = GeneralInfo.objects.filter(Chr__iexact=q_CHR, Start__range=(q_START1, q_START2), End__range=(q_START,q_END1), Organism__iexact=ORG )
                ortho = query_processor(Location_query, ORG )
                LncID = ortho[4]

                Box_Plot = Data_preparation(organism=ORG, lncRNA_Id= LncID)

                if isinstance(ortho, list):
                    return render(request, 'results.html', {'Ids_results':Location_query, 'hsa_ortho':ortho[0], 'pan_ortho':ortho[1], 'gor_ortho':ortho[2], 'gib_ortho':ortho[3], 'graph': Box_Plot, 'browser_org':ORG_Id})
                else:
                    return render(request, 'warnings.html',{'Warn':ortho})               

            else:
                messages.info(request, 'Please specify Location and Organism!')
                return HttpResponseRedirect('/ApplicationExplore/')
        
        ### Sequence based search
        
        if seq_search_form.is_valid() and request.POST.get('Sequences'):
            Sequence = request.POST.get("Sequence")
            database_name = seq_search_form.cleaned_data['Organism_db']
            db_names_str = ', '.join(database_name)
            fasta_filename =  os.path.join(settings.STATIC_DIR,'Tmp','Tmp_sequence.fasta')
            with open(fasta_filename, 'w') as fasta_file:
                fasta_file.write(f'{Sequence}')

            Blast_results = run_blast(fasta_filename, database_name)

            return render(request,'results.html', {'Blast_results': Blast_results, 'Database_selection':db_names_str,})
        
        ### Search based on multiple IDs as input

        if multipleID_search_form.is_valid() and request.POST.get('MultiIds'):
            Multi_IDs = request.POST.get("MultiIDs")
            Organism = request.POST.get("Organism")
            Multi_IDs_list = re.split(r',|\n|\s', Multi_IDs)
            Multi_IDs_list = list(filter(lambda x: x != "", Multi_IDs_list))

            if Multi_IDs and Organism:
                return render(request,'results.html', {'MultiIds_results': Multi_IDs_list, 'Organism':Organism,})
            else:
                messages.info(request, 'Please enter the list and specify the organism!')
                return HttpResponseRedirect('/ApplicationExplore/')

    else:
        id_search_form= ExplorationFormByIDs()
        Loc_search_form = ExplorationForm()
        seq_search_form = ExploreFormSeq()
        multipleID_search_form = ExploreMultipleIds()

    return render(request, 'explore.html', {'form1': id_search_form, 'form2':Loc_search_form, 'form3': seq_search_form, 'form4': multipleID_search_form})
