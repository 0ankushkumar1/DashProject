import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, html
import dash
from dash import html, dcc

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
country = df1.groupby("Country")
# Enter country name to get the data
Unique_Countries = df1["Country"].unique().tolist()
temp_df= country.get_group(Unique_Countries)
temp_df = temp_df.resample("ME").sum().drop(columns=["Country"])
temp_df["Recovered_diff"] = temp_df["Recovered"] - temp_df["Recovered"].shift(1)
temp_df = temp_df[~(np.isnan(temp_df["Recovered_diff"])|temp_df["Recovered_diff"]==0)].drop(columns=["Recovered_diff"])
temp_df = temp_df.iloc[:-1]
px.line(temp_df, x=temp_df.index, y=["Recovered","Deaths","Active Cases"], title="Recovered Cases in Russia",template="plotly_dark",log_y=True)
# Related Variables
Confirmed = temp_df[-1:]["Confirmed"].values[0]
Recovered = temp_df[-1:]["Recovered"].values[0]
Deaths = temp_df[-1:]["Deaths"].values[0]
Active = temp_df[-1:]["Active Cases"].values[0]

df2.set_index("Date", inplace=True)
df2.drop(columns=["Increase rate"], inplace=True)
df2["Recovered_diff"] = df2["Recovered"] - df2["Recovered"].shift(1)
df2 = df2[~(np.isnan(df2["Recovered_diff"])|df2["Recovered_diff"]==0)].drop(columns=["Recovered_diff"])
df2= df2.iloc[:-1]
line = px.line(df2.reset_index(), x="Date", y=["Confirmed","Recovered","Deaths"],title="Global Covid 19 Cases",template="plotly_dark", log_y=True)
df3.reset_index()
df3=df3.rename(columns={"name":"Country","country":"none"}).drop(columns=["none"])
df = df1.merge(df3,on="Country",how="outer")
df = df.dropna()
# Plot the Map 
fig = px.scatter_map(df, lat="latitude", lon="longitude", size="Confirmed", zoom=3,hover_name="Country",hover_data=["Confirmed","Recovered","Deaths"],template="plotly_dark")


app = Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1('Corona Virus Dashboard', style={'text-align': 'center', 'margin': '20px'}),
    html.Div([
        html.Div([
            html.Div([
                # Card 1
                html.Div([
                    
                    html.Div([
                        html.H3("Total Cases", className='text-light'),
                        html.H4(Confirmed, className='text-light')
                    ], className='card-body')
                ], className='card bg-danger mb-4'),
                html.Div([
                    html.Div([
                        html.H3("Active Cases", className='text-light'),
                        html.H4(Active, className='text-light')
                    ], className='card-body')
                ], className='card bg-info mb-4'),
                html.Div([
                    html.Div([
                        html.H3("Recovered", className='text-light'),
                        html.H4(Recovered, className='text-light')
                    ], className='card-body')
                ], className='card bg-warning mb-4'),
                html.Div([
                    html.Div([
                        html.H3("Deaths", className='text-light'),
                        html.H4(Deaths, className='text-light')
                    ], className='card-body')
                ], className='card bg-success mb-4')
            ])
        ], className='col-4', style={'padding': '20px'}),
        html.Div([
            html.Div([
                html.H3("COVID-19 Trends", className='text-center'),
                dcc.Graph(
                    id='covid-trend-graph',
                    figure=line
                )
            ], className='card h-100')
        ], className='col-4', style={'padding': '20px'}),
        html.Div([
            html.Div([
                html.H3("Geographic Distribution", className='text-center'),
                dcc.Graph(
                    id='covid-map',
                    figure=fig
                )
            ], className='card h-100')
        ], className='col-4', style={'padding': '20px'})
    ], className='row')
], style={'margin': '0 auto', 'max-width': '1800px'})

if __name__ == '__main__':
    app.run_server(debug=True)

if __name__ == '_main_':
    app.run_server(debug=True, port=5000)