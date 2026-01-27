import plotly.express as px

def line_plot(df, x, y, hover_data=None):
    fig = px.line(
            df,
            x=x,
            y=y,
            hover_data=hover_data,
            )
    
    # ta bort rutan
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  # Gör bakgrunden helt genomskinlig
        plot_bgcolor="rgba(0,0,0,0)",   # Gör själva plot-ytan genomskinlig
        margin=dict(t=0, l=0, r=0, b=0) # Tar bort all whitespace runt cirkeln
    )

    return fig

def pie_plot(df, x, y):
    fig = px.sunburst(
        df,
        path=[x.name, y.name],
        color=y.name,
        color_discrete_map={'positivt': 'green', 'negativt': 'red'}
    )
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  
        plot_bgcolor="rgba(0,0,0,0)",   
        margin=dict(t=0, l=0, r=0, b=0)
    )
    
    return fig