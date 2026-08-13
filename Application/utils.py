import plotly.express as px


def get_simple_plot(lncRNA_df, lncRNA_id):
    region_order = ['CB', 'STR', 'HIP', 'ACC', 'DPFC', 'VPFC', 'PMC', 'V1C']
    fig = px.box(lncRNA_df, x="Region", y="Log2_Expression", color="Region", category_orders={'Region': region_order})
    graph = fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default

    return graph