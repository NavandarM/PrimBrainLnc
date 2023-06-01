from django.shortcuts import render
from Application.models import GeneralInfo
from .forms import ExplorationFormByIDs, UserMessageForm, ExplorationForm, ExploreFormSeq, ExploreMultipleIds
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
import re
from django.db.models import Q
from django.views.generic import View, TemplateView
import pandas as pd
import numpy as np
import os
from .utils import get_simple_plot
from django.conf import settings
import subprocess
from django.urls import reverse
from django.utils.safestring import mark_safe  # Remove if not used!
from django.utils.html import format_html
from html import unescape

#from django.template  import RequestContext

# Create your views here.


class  IndexView(TemplateView):
    template_name = "index.html"
    def get_context_data(self, **kwargs):
        HomePageContent = super().get_context_data(**kwargs)
        HomePageContent['insert_content'] = 'Welcome to PrimBrainLnc'
        return HomePageContent

# def index(request):
#     Nazara = {'insert_content':"Welcome to PrimBrainLnc!"}

#     return render(request,'index.html', context=Nazara)

def search(request):
    Queries = GeneralInfo.objects.all()
    return render(request, 'search.html', {'Total_Entries':Queries})

def statistics(request):
    return render(request, 'statistics.html')

def downloads(request):
    return render(request, 'downloads.html')

def contact(request):
    return render(request,'contact.html')

def faqs(request):
    return render(request, 'faqs.html')

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

#### Function of splitting the string into specific pattern
def query_processor( query_entity, organism_entity ):

    if query_entity:
        for field in query_entity:
            LncID = field.LncRNA_id
            #human_ortho = entity.Orthologs_Human.replace(';',' ;')
            human_ortho = field.Orthologs_Human.replace(' ','').split(';')
            #chimp_ortho = entity.Orthologs_Chimp.replace(';',' ;')
            chimp_ortho = field.Orthologs_Chimp.replace(' ','').split(';')
            #gorilla_ortho = entity.Orthologs_Gorilla.replace(';',' ;')
            gorilla_ortho = field.Orthologs_Gorilla.replace(' ','').split(';')
            #gibbon_ortho = entity.Orthologs_Gibbon.replace(';',' ;')
            gibbon_ortho = field.Orthologs_Gibbon.replace(' ','').split(';')

            my_list = [ human_ortho, chimp_ortho, gorilla_ortho, gibbon_ortho, LncID ]
            
            return my_list
    else:
        WARN = "No entires found! Probably you entered invalid lncRNA id for " + organism_entity
        return WARN

#### Preparation of the data for visualization

def Data_preparation ( organism, lncRNA_Id ):
    ## File path
    human_file = os.path.join(settings.STATIC_DIR,'files/ExpressionCounts','Normalized_Read_Counts_Human.txt')
    chimp_file = os.path.join(settings.STATIC_DIR,'files/ExpressionCounts', 'Normalized_Read_Counts_Chimp.txt')
    gorilla_file = os.path.join(settings.STATIC_DIR,'files/ExpressionCounts','Normalized_Read_Counts_Gorilla.txt')
    Organism_files = {'Human':human_file, 'Chimp': chimp_file, 'Gorilla': gorilla_file}
    try:
        if organism in Organism_files:
            Exp_data = pd.read_csv(Organism_files[organism], sep="\t")      # Open the file of desired organism
            Exp_data1 = Exp_data.set_index('Ids')                           # Assign Ids are row names
            Entity = Exp_data1.loc[lncRNA_Id].to_frame()                    # Accessing the records of the given lncRNA_Id
            Entity['Region'] = [re.sub(".*_.*.*_", "", name) for name in Entity.index]      # Get the name of region from the columns of the expression data
            Entity['Region'] = [re.sub(".bam.out", "", name) for name in Entity['Region'] ]
            region_order = ['CB', 'STR', 'HIP', 'ACC', 'DPFC', 'VPFC', 'PMC', 'V1C']        # I want to see the boxplot in this specific order
            Entity['Region'] = pd.Categorical(Entity['Region'], categories=region_order, ordered=True)     # It will infer the categories and their order from the input data
            Entity['Log2_Expression'] = np.log2(Entity[lncRNA_Id] +1 )
            
            import plotly.express as px    # we need this package for plotting
            plot_title = 'Expression for ' + lncRNA_Id
            fig = px.box(Entity, x="Region", y="Log2_Expression", color="Region", category_orders={'Region': region_order}, width=850, height=500)
            fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default
            export = fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5 ),
                                        title={'text': plot_title, 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'}, 
                                        yaxis_title= "log2 (Expression)",
                                        xaxis_title= "Regions",
                                        legend_title="" )
            graph= export.to_html()
            return graph

        else:
            graph = "Expression is Not available!"
            return graph
    except:
        print("Not Available!!!")

def Results_from_ids(request, lncIDs, OrgS ):

    ORG= OrgS.capitalize()
    Ids_query = GeneralInfo.objects.all().filter(LncRNA_id__iexact=lncIDs, Organism__iexact=ORG)
    Organism_dictionary = {"Human":"hg19","Chimp":"panTro4","Gorilla":"gorGor4","Gibbon":"nomLeu3"}
    ORG_Id= Organism_dictionary[ORG]
    ortho = query_processor(Ids_query, ORG )
    Box_Plot = Data_preparation(organism=ORG, lncRNA_Id= lncIDs)
    if isinstance(ortho, list):
        return render(request, 'results.html', {'Ids_results':Ids_query, 'hsa_ortho':ortho[0], 'pan_ortho':ortho[1], 'gor_ortho':ortho[2], 'gib_ortho':ortho[3], 'graph': Box_Plot, 'browser_org':ORG_Id})
    else:
        return render(request, 'warnings.html',{'Warn':ortho})


### Run the blast
def run_blast(input_file, database_name):
    ## fasta sequences from organisms to consider
    GenomeFiles = "cat "
    for db_entity in database_name:
        if 'Human' in db_entity:
            path= os.path.join(settings.STATIC_DIR,'files/purelncs','Hsapiens_Pure_lncrnas.fasta')
            GenomeFiles = GenomeFiles + path + ' '
        elif 'Chimp' in db_entity:
            path= os.path.join(settings.STATIC_DIR,'files/purelncs','Chimp_pure_lncRNAs.fasta')
            GenomeFiles = GenomeFiles + path + ' '
        elif 'Gorilla' in db_entity:
            path= os.path.join(settings.STATIC_DIR,'files/purelncs','Gorilla_pure_lncRNAs.fasta')
            GenomeFiles = GenomeFiles + path + ' '
        elif 'Gibbon' in db_entity:
            path= os.path.join(settings.STATIC_DIR,'files/purelncs','Gibbon_pure_lncRNAs.fasta')
            GenomeFiles = GenomeFiles + path + ' '
    
    # All the paths of the files
    Input_genome_pre= os.path.join(settings.STATIC_DIR,'Tmp','GenomePrepInput.fasta')
    GenomeFiles = GenomeFiles + ">" + Input_genome_pre

    blast_path=os.path.join(settings.STATIC_DIR,'softwares/ncbi_blast/bin')
    out_path_db=os.path.join(settings.STATIC_DIR,'Tmp','OrganismDB')
    
    # Command for the customized database
    subprocess.run(GenomeFiles, shell=True)

    makeblastdb_cmd = f"{blast_path}/makeblastdb -in {Input_genome_pre} -dbtype nucl -title organism -out {out_path_db}"
    
    # Execute the blastn command
    subprocess.run(makeblastdb_cmd, shell=True)

    ## Preapration for Blast
    out_path=os.path.join(settings.STATIC_DIR,'Tmp','BLAST_output.txt')

     # Command to run standalone blastn
    blastn_cmd = f"{blast_path}/blastn -query {input_file} -db {out_path_db} -out {out_path} -evalue 0.001 -outfmt 6 -perc_identity 95 -max_target_seqs 20"

    # Execute the blastn command
    subprocess.run(blastn_cmd, shell=True)

    Blast_output = pd.read_csv(out_path,sep='\t', header=None)
    new_headers = ['Query', 'Hit_in_Database', 'Per identity', 'Alignment length', 'Mismatches', 'Gap opens', 'Qurey start', 'Qurey end', 'Hit start', 'Hit end', 'E-value', 'Bit score']
    Blast_output.columns = new_headers
    #Blast_output['Hit_in_Database'] = Blast_output['Hit_in_Database'].apply(create_hyperlink)

    print(Blast_output)
    
    #Blast_output = Blast_output.rename(columns={"Hit_in_Database": "Hit in Database"})  # column renamed
    Blast_output_subset = Blast_output[['Query', 'Hit_in_Database', 'Per identity', 'Alignment length', 'Mismatches', 'Hit start', 'Hit end', 'E-value', 'Bit score']]
    Blast_output_subset['Hit_in_Database'] = Blast_output_subset['Hit_in_Database'].apply(create_hyperlink)
    #Blast_output_subset['Hit_in_Database'] = Blast_output_subset.apply(create_hyperlink, axis=1)

    Blast_output_subset= Blast_output_subset.to_html(index=False, header=True, classes='table table-bordered', justify='center')

    Blast_output_subset = unescape(Blast_output_subset)  ## To get ride of &lt; AND &gt

    print(Blast_output_subset)
    return mark_safe(Blast_output_subset)


# def create_hyperlink(row):
#     lncRNA_Id, Organism = row['Hit_in_Database'].rsplit('_', maxsplit=1)
#     url = f"/Applicationresults_from_ids/{lncRNA_Id}/{Organism}"
#     return format_html('<a href="{}">{}</a>', url, row['Hit_in_Database'])

def create_hyperlink(Hit_in_Database):
    lncRNA_Id, Organism = Hit_in_Database.rsplit('_', 1)
    url = reverse('Application:results-from-ids', args=(lncRNA_Id.strip(), Organism.strip()))
    #hyperlink = format_html('<a href="{}">{}</a>', url, Hit_in_Database)
    #return hyperlink
    
    url = reverse('Application:results-from-ids', args=(lncRNA_Id, Organism))
    return mark_safe(f'<a href="{url}">{Hit_in_Database}</a>')


def split_the_header(query):
    for i in query:
        parts = query[i].split("_")
        if len(parts) == 3:
            output = parts[0] + "_" + parts[1], parts[2]
            print(output)
        else:
            print("Invalid format")


def Explore(request):
    
    if request.method == 'POST':
        id_search_form = ExplorationFormByIDs(request.POST)
        Loc_search_form = ExplorationForm(request.POST)
        seq_search_form = ExploreFormSeq(request.POST)
        multipleID_search_form = ExploreMultipleIds(request.POST)

        ### Id based search

        if id_search_form.is_valid() and request.POST.get('Idss'):
            IDS = request.POST.get("ID").strip()
            ORG = request.POST.get("Organism").capitalize().strip()
            Organism_dictionary = {"Human":"hg19","Chimp":"panTro4","Gorilla":"gorGor4","Gibbon":"nomLeu3"}
            ORG_Id= Organism_dictionary[ORG]

            if IDS and ORG:
                Ids_query = GeneralInfo.objects.all().filter(LncRNA_id__iexact=IDS, Organism__iexact=ORG )
                ortho = query_processor(Ids_query, ORG )
                Box_Plot = Data_preparation(organism=ORG, lncRNA_Id= IDS)
                print(ortho)

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
            print (Overlap)
            if Position and ORG:
                Location_pattern= re.compile(r'(\S+):(\S+)-(\S+)')
                Location_group = Location_pattern.search(Position.replace(" ",""))
                q_CHR, q_START, q_END = Location_group.groups()
                ## To allow overlap:
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
                Organism_dictionary = {"Human":"hg19","Chimp":"panTro4","Gorilla":"gorGor4","Gibbon":"nomLeu3"}
                ORG_Id= Organism_dictionary[ORG]

                #Location_Chr = GeneralInfo.objects.raw( '''Select * from Organism_Table where Chr=%s AND Start=%s AND End= %s''', [Q_CHR, int(Q_START), int(Q_END)] ) 
                #Location_Chr = GeneralInfo.objects.all().filter(Q(Chr=q_CHR), Q(Start__gte=q_START1) | Q(Start__lte=q_START2), Q(End__gte=q_START) | Q(End__lte=q_END1), Q(Organism__iexact=Org) )
                Location_query = GeneralInfo.objects.all().filter(Chr__iexact=q_CHR, Start__range=(q_START1, q_START2), End__range=(q_START,q_END1), Organism__iexact=ORG )
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
        
        if seq_search_form.is_valid() and request.POST.get('Sequences'):
            Sequence = request.POST.get("Sequence")
            database_name = seq_search_form.cleaned_data['Organism_db']
            print(database_name)
            fasta_filename =  os.path.join(settings.STATIC_DIR,'Tmp','Tmp_sequence.fasta')
            with open(fasta_filename, 'w') as fasta_file:
                fasta_file.write(f'{Sequence}')

            Blast_results = run_blast(fasta_filename, database_name)

            # context={

            #             'Query':Blast_results[0],
            #             'Hit_from_db':Blast_results[1],
            #             'Per_identity':Blast_results[2],
            #             'Alignment_length':Blast_results[3],
            #             'mismatches':Blast_results[4],
            #             'Hit_start':Blast_results[8],
            #             'Hit_end':Blast_results[9],
            #             'Evalue':Blast_results[10],
            #             'Bit_score':Blast_results[11],
            #             'Database_selection':database_name,
            #     }
            # GenomePrep= prepareGenome(database_name)

            return render(request,'results.html', {'Blast_results': Blast_results, 'Database_selection':database_name,})
        
        if multipleID_search_form.is_valid() and request.POST.get('MultiIds'):
            Multi_IDs = request.POST.get("MultiIDs")
            Organism = request.POST.get("Organism")
            Multi_IDs_list = re.split(',|\n|\s',Multi_IDs)
            Multi_IDs_list = list(filter(lambda x: x != "", Multi_IDs_list))

            if Multi_IDs and Organism:
                return render(request,'results.html', {'MultiIds_results': Multi_IDs_list, 'Organism':Organism,})
            else:
                messages.info(request, 'Please enter the list and specify the organism!')
                return HttpResponseRedirect('/ApplicationExplore/')

        # if ortho_search_form.is_valid() and request.POST.get('Orthologous'):
        #     Orthologs1= request.POST.get("Orthologs1")
        #     Orthologs2= request.POST.get("Orthologs2")
        #     lncRNAs_id = request.POST.get("lncRNAs_id")
        #     print(Orthologs1)
        #     print(Orthologs2)
        #     print(lncRNAs_id)
        #     Query = OrthoInfy.objects.all().select_related().filter(lncRNA1uid_id__exact="hsa_TCONS_00068882")
        #     #Query="Hello!"
        #     return render(request, 'results.html', {'Result_ortho':Query})

    else:
        id_search_form= ExplorationFormByIDs()
        Loc_search_form = ExplorationForm()
        seq_search_form = ExploreFormSeq()
        multipleID_search_form = ExploreMultipleIds()
        #ortho_search_form = OrthologsForm()

    return render(request, 'explore.html', {'form1': id_search_form, 'form2':Loc_search_form, 'form3': seq_search_form, 'form4': multipleID_search_form})   #'form4': ortho_search_form