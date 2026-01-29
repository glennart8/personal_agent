import plotly.express as px
from utils import get_exploded_keywords
import pandas as pd

def plot_negative_triggers(df):
    all_keywords = get_exploded_keywords(df)
    
    # Filtrera på negativt och räkna förekomst
    neg_counts = all_keywords[all_keywords['mood'] == 'Negativt']['keyword'].value_counts().reset_index()
    neg_counts.columns = ['keyword', 'count']
    neg_counts = neg_counts.head(10)
    
    fig = px.bar(
        neg_counts, 
        x='count', 
        y='keyword',
        orientation='h', # liggande staplaar
        title="Top 10 shitty activities",
        color='count',
        color_continuous_scale='Reds'
    )
    
    # transparent style
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed"), # Mest frekvent högst upp
        margin=dict(t=30, l=0, r=0, b=0),
        xaxis_title=None,
        yaxis_title=None
    )
    
    return fig


def plot_keyword_sunburst(df):
    df_exp = get_exploded_keywords(df)
    
    fig = px.sunburst(
        df_exp,
        path=['mood', 'keyword'], # Först Pos/Neg, sen Aktivitet
        color='mood',
        color_discrete_map={
            'Positivt': 'rgba(0, 128, 0, 0.6)', 
            'Negativt': 'rgba(255, 0, 0, 0.6)'
        }
        
    )
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=0, l=0, r=0, b=0)
    )
    
    fig.update_traces(
        # sätter textfärgen till vit
        insidetextfont=dict(color="white", size=14) 
    )
    
    return fig


# Denna fick jag mycket hjälp av LLM med..
def plot_combined_triggers(df):
    all_keywords = get_exploded_keywords(df)
    
    # räkna antal per mood och keyword
    counts = all_keywords.groupby(['mood', 'keyword']).size().reset_index(name='count')
    top_neg = counts[counts['mood'] == 'Negativt'].nlargest(10, 'count')
    top_pos = counts[counts['mood'] == 'Positivt'].nlargest(10, 'count')
    
    # slå ihop dem
    combined = pd.concat([top_neg, top_pos])
    
    # Gör negativa värden negativa matematiskt (för att de ska peka åt vänster)
    combined['plot_value'] = combined.apply(
        lambda x: -x['count'] if x['mood'] == 'Negativt' else x['count'], axis=1
    )
    
    # sortera
    combined = combined.sort_values(by='plot_value', ascending=True)

    fig = px.bar(
        combined,
        x='plot_value',
        y='keyword',
        orientation='h',
        color='mood',
        color_discrete_map={'Positivt': "#12641D", 'Negativt': "#9E3127"},
        title="Impact of different triggers",
        # Custom data för att visa korrekta siffror i tooltippen (inte minus)
        custom_data=['count']
    )

    # Fixa layouten
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, l=0, r=0, b=0),
        xaxis=dict(
            title=None,
            showticklabels=False, # döljer x-axeln 
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.2)'
        ),
        yaxis=dict(title=None),
        barmode='relative', # för att staplarna ska utgå från mitten
        legend_title=None
    )
    
    # fixar tooltippen så den visar absolutvärdet (t.ex. "5" istället för "-5")
    fig.update_traces(hovertemplate="%{y}: %{customdata[0]}<extra></extra>")

    return fig


def line_plot(df, x, y, hover_data=None):
    fig = px.line(
            df,
            x=x,
            y=y,
            hover_data=hover_data,
            # denna lägger positivt i toppen och negativt i botten (byter plats)
            category_orders={y: ["Positivt", "Negativt"]}
            )
    
    # ta bort rutan
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  # Gör bakgrunden helt genomskinlig
        plot_bgcolor="rgba(0,0,0,0)",   # Gör själva plot-ytan genomskinlig
        margin=dict(t=0, l=0, r=0, b=0) # Tar bort all whitespace runt cirkeln
    )

    return fig

def timeline_plot(df: pd.DataFrame, y: str):
    df = df.copy()
    
    df["date"] = pd.to_datetime(df["date"])
    df["date_end"] = df["date"] + pd.Timedelta(days=1)
    df["mood"] = df["mood"].str.capitalize()
    
    fig = px.timeline(
        df, 
        x_start="date", 
        x_end="date_end", 
        y=y, 
        color=y, 
        hover_name="weekday", 
        color_discrete_map={
            "Positivt": "green",
            "Negativt": "red"},
        hover_data={
                "activity": True,
                "date_end": False,
                "mood": False
                },
        labels={
                "date": "Datum",
                "activity": "Aktivitet",
                "mood": "Mående",
                }
        )
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  
        plot_bgcolor="rgba(0,0,0,0)",   
        margin=dict(t=0, l=0, r=0, b=0)
    )
    
    return fig

def pie_plot(df, x, y):
    fig = px.sunburst(
        df,
        path=[x.name, y.name],
        color=y.name,
        color_discrete_map={'Positivt': 'green', 'Negativt': 'red'}
    )
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  
        plot_bgcolor="rgba(0,0,0,0)",   
        margin=dict(t=0, l=0, r=0, b=0)
    )
    
    return fig