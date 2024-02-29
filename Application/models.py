from operator import length_hint
from tkinter import CASCADE
from tokenize import Name
from django.db import models
from django.forms import EmailField


# General information of lncRNAs

class GeneralInfo(models.Model):
    LncRNA_id = models.CharField(max_length=25)
    LncRNA_uid = models.CharField(max_length=50, primary_key=True, unique=True)
    Chr = models.CharField(max_length=50)
    Start = models.BigIntegerField()
    End = models.BigIntegerField()
    Strand = models.CharField(max_length=2)
    TSS = models.CharField(max_length=50)
    Promoter_start = models.CharField(max_length=50)
    Promoter_end = models.CharField(max_length= 50)
    Length = models.CharField(max_length=50)
    Exon_number = models.CharField(max_length=50)
    Tr_Class = models.CharField(max_length=25)
    Tr_Direction = models.CharField(max_length=150)
    Tr_Location = models.CharField(max_length=150)
    Expression_status = models.CharField(max_length=150)
    Orthologs_status = models.CharField(max_length=150)
    Overlap_gene_id = models.CharField(max_length=150)
    Overlap_ref_id = models.CharField(max_length=150)
    Class_code = models.CharField(max_length=5)
    Organism = models.CharField(max_length=15)
    Orthologs_Human = models.CharField(max_length=1000)
    Orthologs_Chimp = models.CharField(max_length=1000)
    Orthologs_Gorilla = models.CharField(max_length=1000)
    Orthologs_Gibbon = models.CharField(max_length=1000)
    DEG_Human = models.CharField(max_length=800)
    DEG_Chimp = models.CharField(max_length=800)
    Sequence= models.TextField()

    def __str__(self):
        return self.LncRNA_uid
    
    class Meta:
        db_table= "General_Info"


class UserOpinion(models.Model):
    Name= models.CharField(max_length=25)
    Email=models.EmailField()
    Phone=models.CharField(max_length=25, blank=True)
    Organization= models.CharField(max_length=100, blank=True)
    Description= models.TextField(blank=True)

    def __str__(self):
        return self.Name
