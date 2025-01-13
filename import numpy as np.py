import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from pathlib import Path

class CovidDashboard:
    def __init__(self):
        self.external_stylesheets = [
            {
                'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css',
                'rel': 'stylesheet',
                'integrity': 'sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJU2nIbbVYUew+Or5vKZ5v2xX',
                'crossorigin': 'anonymous'
            }
        ]
        self.app = Dash(__name__, external_stylesheets=self.external_stylesheets)
        self.load_data()
        self.process_data()
        self.setup_layout()
        self.setup_callbacks()

    def load_data(self):
        # Using Path for platform-independent file paths
        data_dir = Path("Dataset")
        self.df_countries = pd.read_csv(data_dir / "countries-aggregated.csv")
        self.df_worldwide = pd.read_csv(data_dir / "worldwide-aggregate.csv")
        self.df_locations = pd.read_csv(data_dir / "countries.csv")

    def process_data(self):
        # Process countries data
        self.df_countries["Date"] = pd.to_datetime(self.df_countries["Date"])
        self.df_countries.set_index("Date", inplace=True)
        self.df_countries.sort_index(inplace=True)
        self.df_countries["Active Cases"] = (
            self.df_countries["Confirmed"] - 
            self.df_countries["Recovered"] - 
            self.df_countries["Deaths"]
        )

        # Process worldwide data
        self.df_worldwide["Date"] = pd.to_datetime(self.df_worldwide["Date"])
        self.df_worldwide.set_index("Date", inplace=True)
        self.df_worldwide.drop(columns=["Increase rate"], inplace=True)

        # Process location data
        self.df_locations = self.df_locations.rename(
            columns={"name": "Country"}
        ).drop(columns=["country"])

        # Merge location data with countries data
        self.df_merged = self.df_countries.merge(
            self.df_locations, on="Country", how="outer"
        ).dropna()

    def get_country_stats(self, country="US"):
        country_data = self.df_countries[self.df_countries["Country"] == country].iloc[-1]
        return {
            "Confirmed": int(country_data["Confirmed"]),
            "Recovered": int(country_data["Recovered"]),
            "Deaths": int(country_data["Deaths"]),
            "Active": int(country_data["Active Cases"])
        }

    def create_country_trend(self, country="US"):
        country_data = self.df_countries[self.df_countries["Country"] == country]
        fig = px.line(
            country_data,
            x=country_data.index,
            y=["Confirmed", "Recovered", "Deaths", "Active Cases"],
            title=f"COVID-19 Trends in {country}",
            template="plotly_dark",
            log_y=True
        )
        return fig

    def create_world_map(self):
        latest_data = self.df_merged.groupby("Country").last().reset_index()
        fig = px.scatter_mapbox(
            latest_data,
            lat="latitude",
            lon="longitude",
            size="Confirmed",
            hover_name="Country",
            hover_data=["Confirmed", "Recovered", "Deaths"],
            zoom=2,
            template="plotly_dark",
            mapbox_style="carto-darkmatter"
        )
        return fig

    def setup_layout(self):
        stats = self.get_country_stats()
        self.app.layout = html.Div([
            html.H1('COVID-19 Dashboard', 
                   className='text-center my-4'),
            
            # Country selector
            html.Div([
                html.Label('Select Country:'),
                dcc.Dropdown(
                    id='country-selector',
                    options=[{'label': country, 'value': country} 
                            for country in sorted(self.df_countries['Country'].unique())],
                    value='US',
                    className='mb-4'
                )
            ], className='container'),
            
            # Stats cards
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Total Cases", className='text-light'),
                        html.H4(id='total-cases', children=stats["Confirmed"], 
                               className='text-light')
                    ], className='card-body')
                ], className='card bg-danger col-md-3'),
                
                html.Div([
                    html.Div([
                        html.H3("Active Cases", className='text-light'),
                        html.H4(id='active-cases', children=stats["Active"], 
                               className='text-light')
                    ], className='card-body')
                ], className='card bg-info col-md-3'),
                
                html.Div([
                    html.Div([
                        html.H3("Recovered", className='text-light'),
                        html.H4(id='recovered-cases', children=stats["Recovered"], 
                               className='text-light')
                    ], className='card-body')
                ], className='card bg-warning col-md-3'),
                
                html.Div([
                    html.Div([
                        html.H3("Deaths", className='text-light'),
                        html.H4(id='death-cases', children=stats["Deaths"], 
                               className='text-light')
                    ], className='card-body')
                ], className='card bg-success col-md-3')
            ], className='row container-fluid my-4'),
            
            # Graphs
            html.Div([
                dcc.Graph(id='country-trend'),
                dcc.Graph(id='world-map', figure=self.create_world_map())
            ], className='container-fluid')
        ])

    def setup_callbacks(self):
        @self.app.callback(
            [Output('total-cases', 'children'),
             Output('active-cases', 'children'),
             Output('recovered-cases', 'children'),
             Output('death-cases', 'children'),
             Output('country-trend', 'figure')],
            [Input('country-selector', 'value')]
        )
        def update_stats(country):
            stats = self.get_country_stats(country)
            trend = self.create_country_trend(country)
            return (
                stats["Confirmed"],
                stats["Active"],
                stats["Recovered"],
                stats["Deaths"],
                trend
            )

    def run(self, debug=True, port=5000):
        self.app.run_server(debug=debug, port=port)

if __name__ == '__main__':
    dashboard = CovidDashboard()
    dashboard.run()