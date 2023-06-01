from dataclasses import fields
from logging import PlaceHolder
from unittest.util import _MAX_LENGTH
from django import forms
from django.forms import ModelForm
from .models import UserOpinion, GeneralInfo
from django.core import validators
import re
from django.utils.safestring import mark_safe
from django.forms import RadioSelect


## Validator functions

# 1. For LncRNA locations:

def check_for_location(value):
    tmp_v1 = value.split(":")
    tmp_v2 = tmp_v1[1].split("-")
    if ( tmp_v2[0].strip().isdigit() and tmp_v2[1].strip().isdigit() ) and ('chr' in tmp_v1[0].lower()):
        print("Location: Correct Format!")
    else:
        raise forms.ValidationError("Please correct location as per Example: Chr1:1231-1413")

# 2. For Organism:

def confirm_organism(value):
    Organism_list = ['Human', 'Chimp','Gorilla','Gibbon']
    if value.capitalize() not in Organism_list:
        raise forms.ValidationError("Please enter the correct name")



## Creat a User Opinion form:

class UserMessageForm(ModelForm):
    class Meta:
        model=UserOpinion
        fields= "__all__"
        
        labels={
            'Name': '',
            'Email':'',
            'Phone':'',
            'Organization':'',
            'Description':'',
        }
        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Name' }),
            'Email': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Email'}),
            'Phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Phone' }),
            'Organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Organization'}),
            'Description': forms.Textarea(attrs={'class': 'form-control', 'placeholder':'Suggestion', 'rows':5}),
                }
    botcatcher = forms.CharField(required=False, widget=forms.HiddenInput)
    def clean_botcatcher(self):
        botcatcher = self.cleaned_data['botcatcher']
        if len(botcatcher) > 0:
            raise forms.ValidationError("Invalid form!")
        return botcatcher

#####################################
#### Forms with search section ######
#####################################


class ExplorationFormByIDs(forms.Form):
    ID = forms.CharField(required=False, max_length=30, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'TCONS_00000001'}), label=mark_safe("<strong>Id</strong>"))
    #Organism= forms.CharField(required=True,max_length=15, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter organism from List: Human, Chimp, Gorilla and Gibbon','style':'max-width: 24em'}), validators=[confirm_organism], label=mark_safe("Organism (required)"))
    organism_choices = [('Human', 'Human'), ('Chimp', 'Chimpanzee'), ('Gorilla', 'Gorilla'), ('Gibbon', 'Gibbon')]
    Organism= forms.ChoiceField(choices=organism_choices, required=False, widget=forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select an organism'}), label="Select an organism")
    def clean(self):
        cleaned_data = super().clean()
        ID=cleaned_data.get("ID")
        Organism=cleaned_data.get("Organism")    

class ExplorationForm(forms.Form):

    Location= forms.CharField(required=False,max_length=100, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Chr1:123243-234235', 'style':'max-width: 24em'}),validators=[check_for_location], label=mark_safe("Chromosome co-ordinates"),)
    #Organism= forms.CharField(required=True,max_length=10, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter organism from List: Human, Chimpanzee, Gorilla and Gibbon','style':'max-width: 24em'}), validators=[confirm_organism], label=mark_safe("Organism (required)"))
    organism_choices = [('Human', 'Human'), ('Chimp', 'Chimpanzee'), ('Gorilla', 'Gorilla'), ('Gibbon', 'Gibbon')]
    Organism= forms.ChoiceField(choices=organism_choices, required=False, widget=forms.Select(attrs={'class': 'form-select', 'style':'max-width: 24em'}), label= "Select an organism")
    Overlap = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class':'form-control','style':'max-width: 12em'}), label=mark_safe("Overlap allowed:"))
    def clean(self):
        cleaned_data = super().clean()
        Location = cleaned_data.get("Location")
        Organism = cleaned_data.get("Organism")
        Overlap = cleaned_data.get("Overlap")

class ExploreFormSeq(forms.Form):
    Sequence = forms.CharField(required=False,widget=forms.Textarea(attrs={'class': 'form-control','rows':5,'placeholder':'>Fasta_header \n ATCGTACGTGCAGATGATGCA'}), label=mark_safe("<strong>Sequence (Blast search)</strong>"))
    organism_choices = [('Human', 'Human'), ('Chimp', 'Chimpanzee'), ('Gorilla', 'Gorilla'), ('Gibbon', 'Gibbon')]
    Organism_db= forms.MultipleChoiceField(choices=organism_choices, required=False, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check form-check-inline',}), label="Select database")
    def clean(self):
        cleaned_data = super().clean()
        Sequence = cleaned_data.get("Sequence")

class ExploreMultipleIds(forms.Form):
    MultiIDs = forms.CharField(required=False,widget=forms.Textarea(attrs={'class': 'form-control','rows':5,'placeholder':'Enter multiple Ids'}), label=mark_safe("<strong>Multiple Ids</strong>"))
    organism_choices = [('Human', 'Human'), ('Chimp', 'Chimpanzee'), ('Gorilla', 'Gorilla'), ('Gibbon', 'Gibbon')]
    Organism= forms.ChoiceField(choices=organism_choices, required=False, widget=forms.Select(attrs={'class': 'form-select'}), label=mark_safe("<strong>Select an organism</strong>"))
    def clean(self):
        cleaned_data = super().clean()
        ID=cleaned_data.get("MultiIds")
        Organism=cleaned_data.get("Organism")

# class OrthologsForm(forms.Form):
#     OrgList =[
#         ('Select','Organism'),
#         ('Human','Human/hsa'),
#         ('Chimp','Chimp/pan'),
#         ('Gorilla','Gorilla/gor'),
#         ('Gibbon','Gibbon/gib'),
#     ]
#     Orthologs1 = forms.ChoiceField(required=False, choices= OrgList, label=mark_safe("<strong>Orthologs</strong>") )
#     Orthologs2 = forms.ChoiceField(required=False, choices= OrgList, label=mark_safe("<strong>Orthologs</strong>") )
#     lncRNAs_id = forms.CharField(required=False, max_length=30 )
#     def clean(self):
#         cleaned_data = super().clean()
#         Orthologs = cleaned_data.get("Orthologs")