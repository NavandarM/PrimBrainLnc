import pandas as pd
import numpy as np
import matplotlib.pyplot as plt  
import plotly.express as px
#import seaborn as sns
from io import BytesIO
import base64

def get_image():
    # Create a bytes buffer for the image to save
    buffer = BytesIO()
    # Create the plot with the use of BytesIO object as its 'file'
    plt.savefig(buffer, format='png')
    # set the cursir the begining of script
    buffer.seek(0)
    # retrive the entire content of the 'file'
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    # free the memory of the buffer
    buffer.close()

    return graph

def get_simple_plot(lncRNA_df, lncRNA_id):
    
    plt.switch_backend('AGG')
    fig = plt.figure(figsize=(10,5))
    
    ax = lncRNA_df.boxplot(column='Log2_Expression',by='Region', grid=True)
    
    title = 'Expression of ' + lncRNA_id
    ax.set_title('')
    ax.set_ylabel('log2(Expression)')
    plt.suptitle('')

    graph = get_image()

    return graph


def get_simple_plot(lncRNA_df, lncRNA_id):
    df = px.data.tips()
    region_order = ['CB', 'STR', 'HIP', 'ACC', 'DPFC', 'VPFC', 'PMC', 'V1C']
    fig = px.box(lncRNA_df, x="Region", y="Log2_Expression", color="Region", category_orders={'Region': region_order})
    graph = fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default

    return graph