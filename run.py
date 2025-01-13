import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash

external_stylesheets = [
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJU2nIbbVYUew+Or5vKZ5v2xX',
        'crossorigin': 'anonymous'
    }
]

# Data Analysis
df1 = pd.read_csv("C:/Users/00010/Desktop/Projects/Covid 19 Dashboard using Plotly and Dash/Dataset/countries-aggregated.csv")
df2 = pd.read_csv("C:/Users/00010/Desktop/Projects/Covid 19 Dashboard using Plotly and Dash/Dataset/worldwide-aggregate.csv")
df3 = pd.read_csv("C:/Users/00010/Desktop/Projects/Covid 19 Dashboard using Plotly and Dash/Dataset/countries.csv")

# Cleaning and Preprocessing
df1["Date"] = pd.to_datetime(df1["Date"])
df1.set_index("Date", inplace=True)
df1.sort_index(inplace=True)
df1["Active Cases"] = df1["Confirmed"] - df1["Recovered"] - df1["Deaths"]

# Get list of countries for dropdown
available_countries = sorted(df1["Country"].unique())

# Initialize app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Process worldwide data
df2.set_index("Date", inplace=True)
df2.drop(columns=["Increase rate"], inplace=True)
df2["Recovered_diff"] = df2["Recovered"] - df2["Recovered"].shift(1)
df2 = df2[~(np.isnan(df2["Recovered_diff"])|df2["Recovered_diff"]==0)].drop(columns=["Recovered_diff"])
df2 = df2.iloc[:-1]

# Create initial global line plot
line = px.line(df2.reset_index(), x="Date", y=["Confirmed","Recovered","Deaths"],
               title="Global Covid 19 Cases", template="plotly_dark", log_y=True)

# Process geographic data
df3.reset_index()
df3 = df3.rename(columns={"name":"Country","country":"none"}).drop(columns=["none"])
df = df1.merge(df3, on="Country", how="outer")
df = df.dropna()

# Plot the Map 
fig = px.scatter_map(df, lat="latitude", lon="longitude", size="Confirmed", zoom=3,
                     hover_name="Country", hover_data=["Confirmed","Recovered","Deaths"],
                     template="plotly_dark")

app.layout = html.Div([
    html.H1('COVID-19 Dashboard', style={
        'text-align': 'center',
        'margin': '20px',
        'color': 'white'
    }),

    # Country Selection Dropdown
    html.Div([
        html.Label('Select Country:', style={
            'margin-right': '10px',
            'color': 'white',
            'font-weight': 'bold'
        }),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country, 'value': country} for country in available_countries],
            value=available_countries[0],
            style={'width': '300px'}
        )
    ], style={'margin': '20px', 'textAlign': 'center'}),

    # First horizontal section - Cards
    html.Div([
        html.Div(id='cards-container', style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'padding': '20px',
            'gap': '10px'
        })
    ], style={
        'height': '25vh',
        'padding': '10px',
        'background-color': '#222222'
    }),

    # Second horizontal section - Graph
    html.Div([
        html.Div([
            html.H3("COVID-19 Trends", style={
                'color': 'white',
                'textAlign': 'center'
            }),
            dcc.Graph(
                id='covid-trend-graph',
                style={'height': '55vh'}
            )
        ], style={'margin': '20px', 'height': '55vh'})
    ], style={'padding': '10px', 'background-color': '#222222'}),

    # Third horizontal section - Map
    html.Div([
        html.Div([
            html.H3("Geographic Distribution", style={
                'color': 'white',
                'textAlign': 'center'
            }),
            dcc.Graph(
                id='covid-map',
                figure=fig.update_layout(height=750),
                style={'height': '65vh'}
            )
        ], style={'margin': '20px', 'height': '65vh'})
    ], style={'padding': '10px', 'background-color': '#222222'})
], style={
    'height': '100vh',
    'margin': '0 auto',
    'maxWidth': '1800px',
    'background-color': '#111111',
    'padding': '10px'
})


@app.callback(
    [Output('cards-container', 'children'),
     Output('covid-trend-graph', 'figure')],
    [Input('country-dropdown', 'value')]
)
def update_metrics(selected_country):
    # Using original logic for data processing
    country = df1.groupby("Country")
    temp_df = country.get_group(selected_country)
    temp_df = temp_df.resample("ME").sum()
    temp_df["Recovered_diff"] = temp_df["Recovered"] - temp_df["Recovered"].shift(1)
    temp_df = temp_df[~(np.isnan(temp_df["Recovered_diff"])|temp_df["Recovered_diff"]==0)].drop(columns=["Recovered_diff"])
    temp_df = temp_df.iloc[:-1]
    
    # Get latest values for cards
    Confirmed = temp_df[-1:]["Confirmed"].values[0]
    Recovered = temp_df[-1:]["Recovered"].values[0]
    Deaths = temp_df[-1:]["Deaths"].values[0]
    Active = temp_df[-1:]["Active Cases"].values[0]
    
    # Create cards
    cards = [
        html.Div([
            html.Div([
                html.H3("Total Cases", className='text-light'),
                html.H4(f"{int(Confirmed):,}", className='text-light')
            ], className='card-body')
        ], className='card bg-danger', style={'flex': '1', 'margin': '0 10px'}),
        
        html.Div([
            html.Div([
                html.H3("Active Cases", className='text-light'),
                html.H4(f"{int(Active):,}", className='text-light')
            ], className='card-body')
        ], className='card bg-info', style={'flex': '1', 'margin': '0 10px'}),
        
        html.Div([
            html.Div([
                html.H3("Recovered", className='text-light'),
                html.H4(f"{int(Recovered):,}", className='text-light')
            ], className='card-body')
        ], className='card', style={
            'flex': '1', 
            'margin': '0 10px',
            'backgroundColor': '#28a745'
        }),
        
        html.Div([
            html.Div([
                html.H3("Deaths", className='text-light'),
                html.H4(f"{int(Deaths):,}", className='text-light')
            ], className='card-body')
        ], className='card bg-dark', style={'flex': '1', 'margin': '0 10px'})
    ]
    
    # Create line plot
    line_plot = px.line(temp_df, x=temp_df.index, y=["Recovered","Deaths","Active Cases"],
                       title=f"COVID-19 Cases in {selected_country}",
                       template="plotly_dark", log_y=True)
    
    line_plot.update_layout(height=700)
    
    return cards, line_plot

if __name__ == '__main__':
    app.run_server(debug=True)

if __name__ == '_main_':
    app.run_server(debug=True, port=5000)