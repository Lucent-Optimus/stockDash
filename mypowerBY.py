import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, ctx
import dash_ag_grid as dag
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from scipy.interpolate import make_interp_spline
import dash_daq as daq
import requests
import re

from dash.exceptions import PreventUpdate

# Load your data
#df = pd.read_csv("BATCH.csv")
df = pd.read_csv("BATCH.csv", encoding='ISO-8859-1')  # or try cp1252
df_buysell = pd.read_csv("BUYSELL.csv", encoding='ISO-8859-1')  # or try cp1252

unique_sectors = df['Sector'].dropna().unique()

graph_properties = {
    'mirror': True,
    'ticks': 'outside',
    'showline': True,
    'linecolor': 'lightgrey',
    'gridcolor': 'lightgrey'
}

#Menu options
menuitems = [
    dbc.DropdownMenuItem("Get Token ID"),
    dbc.DropdownMenuItem("Another action"),
    dbc.DropdownMenuItem("Something else here"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("About Stock Analyser"),
]


# Calculate totals
sector_profits = df.groupby("Sector")["Total Profit"].sum()
total_profit_all = sector_profits.sum()
selected_company=""

# Generate sector cards
sector_cards = [
    dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.H5(sector, className="card-title"),
                html.H6(f"£{profit:,.2f}", className="card-subtitle text-success mb-0")
            ]),
            className="h-100 w-100",
            style={
                "textAlign": "center",
                "minHeight": "140px",
                "border": "1px solid #dee2e6",
                "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
                "borderRadius": "6px"
            }
        ),
        width=2,
        className="d-flex align-items-stretch mb-3"
    )
    for sector, profit in sector_profits.items()
]

# Wrap it all in one outer card
sector_summary_card = dbc.Card(
    dbc.CardBody([
        
        html.H4(f"Total Profit: £{total_profit_all:,.2f}", className="text-primary mb-4"),
        html.H5("Sector Overview", className="mb-3"),
        dbc.Row(sector_cards, className="gx-3", align="stretch")
    ]),
    className="mb-4",
    style={"backgroundColor": "#f8f9fa"}
)

# Insert into your homepage_content layout
honepage_content = dbc.Card(
    dbc.CardBody([
        html.Div(
            style={
                'background-image': 'url("/assets/wwwhirl.svg")',
                'background-size': '1000px auto',
                'background-repeat': 'no-repeat',
                'height': '120vh',
                'display': 'flex',
                'flexDirection': 'column',
                'color': 'black',
                'font-size': '16px',
                'padding': '20px'
            },
            children=[
                dbc.Col([
                   #html.H1("Stock Dash"),
                   dbc.Row(sector_summary_card, className="gx-3", align="stretch"),
                   html.Br(),
                   html.P("Stock Dash takes the output of a proprietary, in-house developed algorithm, designed to pinpoint precise BUY and SELL signals for each stock listed in the London Stock Exchange."),
                   html.Br(),
                ], width=12)
            ]
        )
    ]),
    className="mt-3"
)

propage_content = dbc.Card(
    dbc.CardBody([
        # ── Sector Buttons
        dbc.Row([
            dbc.Col(id="sector-button-container")
        ], className="my-3"),

        # ── Sector Selection Store
        dcc.Store(
            id="selected-sector-store",
            data=unique_sectors[0] if len(unique_sectors) > 0 else None
        ),

        # ── Bar Chart
        dbc.Row([
            dbc.Col(
                dcc.Graph(id="bar-graph", style={"border": "1px solid #D3D3D3"})
            )
        ]),

        # ── Company & Industry Table
        dbc.Row([
            dbc.Col([
                dag.AgGrid(
                    id="company_industry_list",
                    columnDefs=[
                        {"field": "Ticker", "minWidth": 90, "maxWidth": 90},
                        {"field": "Name", "minWidth": 240, "maxWidth": 240},
                        {"field": "Industry", "minWidth": 240, "maxWidth": 240},
                        {"field": "Avg Hold Period(days)", "minWidth": 190, "maxWidth": 190},
                        {"field": "BUY Range", "minWidth": 150, "maxWidth": 150},
                        {"field": "SELL Range", "minWidth": 150, "maxWidth": 150},
                        {"field": "Price Movement", "minWidth": 150, "maxWidth": 150},
                        {"field": "Total Profit", "minWidth": 110, "maxWidth": 110}
                    ],
                    rowData=df.to_dict("records"),
                    columnSize="sizeToFit",
                    dashGridOptions={"rowSelection": "single"},
                    style={"height": "400px", "width": "100%"},
                    className="ag-theme-alpine"
                )
            ])
        ], className="mt-3"),

        # ── BUY/SELL Dashboard Tabs
        dbc.Tabs([
            dbc.Tab(
                id="dynamic-tab",
                label="No Data",
                label_style={
                    "fontWeight": "bold",
                    "border": "none",
                    "boxShadow": "none",
                    "backgroundColor": "#ffffff"
                },
                children=[
                    dbc.Row([
                        # ── BUY/SELL Table
                        dbc.Col([
                            dbc.Tabs([
                                dbc.Tab(
                                    label="BUY / SELL Signals",
                                    children=[
                                        dbc.Row([
                                            dbc.Col([
                                            
                                                dcc.Loading(
                                                    id="loadingbuy-sell-table",
                                                    type="default",
                                                    children=[
                                            
                                                        dag.AgGrid(
                                                            id="buy-sell-table",
                                                            rowData=[],
                                                            columnDefs=[
                                                                {"field": "Ticker", "minWidth": 90, "maxWidth": 90},
                                                                {"field": "Date", "minWidth": 190, "maxWidth": 190},
                                                                    {
                                                                    "field": "Signal",
                                                                    "minWidth": 75,
                                                                    "maxWidth": 75,
                                                                    "cellClassRules": {
                                                                        "green-text": 'params.value === "Buy"',
                                                                        "red-text": 'params.value === "Sell"',
                                                                        "bold-text": 'params.value === "Total"'
                                                                        }
                                                                    },
                                                                {"field": "Price", "minWidth": 90, "maxWidth": 90},
                                                                {"field": "Invested", "minWidth": 90, "maxWidth": 90},
                                                                {"field": "Shares", "minWidth": 90, "maxWidth": 90},
                                                                {"field": "Avg Price", "minWidth": 100, "maxWidth": 100},
                                                                {
                                                                    "field": "Profit",
                                                                    "minWidth": 100,
                                                                    "maxWidth": 100,
                                                                    "cellClassRules": {
                                                                        "bold-profit": "params.data.is_summary === true"
                                                                    }
                                                                }
                                                            ],
                                                            className="ag-theme-alpine",
                                                            style={"height": "400px", "width": "100%", "paddingTop": "5px"},
                                                            defaultColDef={"resizable": True},
                                                            columnSize="sizeToFit"
                                                        )]
                                                )
                                            ], width=8),

                                            # ── Right: Gauges
                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        dbc.Row([
                                                            dbc.Col(
                                                                daq.Gauge(
                                                                    id="volume-gauge",
                                                                    label="Volume Indicator",
                                                                    min=0,
                                                                    max=10,
                                                                    value=0,
                                                                    color={
                                                                        "gradient": True,
                                                                        "ranges": {
                                                                            "red": [0, 3],
                                                                            "yellow": [3, 6],
                                                                            "green": [6, 10]
                                                                        }
                                                                    },
                                                                    size=160
                                                                )
                                                            ),
                                                            dbc.Col(
                                                                daq.Gauge(
                                                                    id="beta-gauge",
                                                                    label="Beta Risk",
                                                                    min=-5,
                                                                    max=5,
                                                                    value=0,
                                                                    color={
                                                                        "ranges": {
                                                                            "#FF3330": [-5, -2.5],
                                                                            "#FFA500": [-2.5, -1],
                                                                            "#00CC66": [-1, 1],
                                                                            "#FFA501": [1, 2.5],
                                                                            "#FF3333": [2.5, 5]
                                                                        }
                                                                    },
                                                                    size=160
                                                                )
                                                            )
                                                        ], className="g-3", justify="center")
                                                    ),
                                                    style={
                                                        "border": "1px solid #D3D3D3",
                                                        "backgroundColor": "#ffffff"
                                                    }
                                                ),
                                                width=4,
                                                className="d-flex align-items-center justify-content-center"
                                            )
                                        ])
                                    ]
                                ),
                                dbc.Tab(dcc.Graph(id="line-graph"), label="Line Chart", style={"border": "1px solid #D3D3D3", "paddingTop": "5px"}),
                                dbc.Tab(
                                    label="MACD",
                                    children=[
                                        html.Div([
                                            dcc.Graph(
                                                id="macd-graph",
                                                style={"border": "1px solid #D3D3D3", "paddingTop": "5px"}
                                            ),

                                        html.Details([
                                            html.Summary('Moving Average Convergence Divergence (MACD)'),
                                            html.Div([
                                                html.P("The MACD graph displays the MACD line, the signal line, and the smoothed momentum."),
                                                html.P("The MACD line crossing above or below the signal line can signal trend changes."),
                                                html.P("The shaded area represents the smoothed momentum (positive or negative)."),
                                            ])
                                        ], style={
                                            'border': '1px solid grey',
                                            'border-radius': '10px',
                                            'padding': '10px',
                                            'width': 'fit-content',
                                            'marginTop': '10px'})
                                        ])
                                    ],
                                    style={"border": "1px solid #D3D3D3", "paddingTop": "5px"}
                                ),                                
                                #dbc.Tab(dcc.Graph(id="macd-graph"), label="MACD", style={"border": "1px solid #D3D3D3", "paddingTop": "5px"}),
                                
                                dbc.Tab(
                                    label="RSI",
                                    children=[
                                        html.Div([
                                            dcc.Graph(
                                                id="rsi-graph",
                                                style={"border": "1px solid #D3D3D3", "paddingTop": "5px"}
                                            ),

                                            html.Details([
                                                html.Summary('Relative Strength Index (RSI)'),
                                                html.Div([
                                                            html.P("RSI shows the relative strength index over time."),
                                                            html.P("(RSI) is a popular momentum indicator used in technical analysis to assess the speed and magnitude of price changes"),
                                                            html.P("RSI  above 70% typically indicate an overbought condition (potential reversal downward),"),
                                                            html.P("while values below 30% suggest an oversold condition (potential reversal upward)"),
                                                ])
                                            ], style={
                                                    'border': '1px solid grey',
                                                    'border-radius': '10px',
                                                    'padding': '10px',
                                                    'width': 'fit-content',
                                                    'marginTop': '10px'
                                                })
                                        ])
                                    ],
                                    style={"border": "1px solid #D3D3D3", "paddingTop": "5px"}
                                ),
                                
                                dbc.Tab(
                                    label="EMA",
                                    children=[
                                        html.Div([
                                            dcc.Graph(
                                                id="ema-graph",
                                                style={"border": "1px solid #D3D3D3", "paddingTop": "5px"}
                                            ),

                                            html.Details([
                                                html.Summary('Exponential Moving Average (EMA)'),
                                                html.Div([
                                                    html.P("EMA is the average price over a specific period and adjusted to give weight to recent prices."),
                                                    html.P("A smoothing factor is used to determine the weight given to the most recent data."),
                                                    html.P("When a shorter-term EMA crosses above a longer-term EMA, it can signal a buy opportunity, and vice versa for a sell signal."),
                                                ])
                                            ], style={
                                                'border': '1px solid grey',
                                                'border-radius': '10px',
                                                'padding': '10px',
                                                'width': 'fit-content',
                                                'marginTop': '10px'
                                            })
                                        ])
                                    ],
                                    style={"border": "1px solid #D3D3D3", "paddingTop": "5px"}
                                )

                            ])
                        ])
                    ])
                ]
            )
        #], className="mt-4", style={"backgroundColor": "#ffffff"})
        ], className="mt-4")
    ]),
    style={"backgroundColor": "#f8f9fa"},
    className="mb-4"
)


advanced_filter = html.Div([
    dbc.Container([
        # Store for user filter selections
        dcc.Store(id="advanced-filter-store"),

        # ── Filter Controls
        dbc.Row([
            dbc.Col([
                html.Label("Sector"),
                dcc.Dropdown(
                    id="filter-sector",
                    options=[{"label": s, "value": s} for s in sorted(df["Sector"].dropna().unique())],
                    multi=True,
                    placeholder="Select Sector"
                )
            ]),
            dbc.Col([
                html.Label("Industry"),
                dcc.Dropdown(
                    id="filter-industry",
                    options=[{"label": i, "value": i} for i in sorted(df["Industry"].dropna().unique())],
                    multi=True,
                    placeholder="Select Industry"
                )
            ])
        ], className="mb-3", style={"marginTop": "1.5rem"}),

        dbc.Row([
            dbc.Col([
                html.Label("Avg Hold Period (days)"),
                dcc.RangeSlider(
                    id="filter-hold-period",
                    min=int(df["Avg Hold Period(days)"].min()),
                    max=int(df["Avg Hold Period(days)"].max()),
                    value=[
                        int(df["Avg Hold Period(days)"].min()),
                        int(df["Avg Hold Period(days)"].max())
                    ],
                    marks=None,
                    tooltip={"placement": "bottom", "always_visible": False}
                )
            ])
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                html.Label("Volume Indicator"),
                dcc.RangeSlider(
                    id="filter-volume",
                    min=0, max=10,
                    value=[0, 10],
                    step=1,
                    #marks={i: str(i) for i in range(0, 11)},
                )
            ], style={"marginTop": "2rem"}),
    
            dbc.Col([
                html.Div(id="Beta-Risk-label", style={"fontWeight": "bold", "marginBottom": "0.5rem"}),
                html.Label("Beta Risk"),
                dcc.RangeSlider(
                    id="filter-beta",
                    min=-5, max=5,
                    allowCross=False,
                    value=[-1, 1],
                    step=0.1,
                    marks={i: str(i) for i in range(-5, 6)}
                )
            ]),
        
            dbc.Col([
                html.Div(id="last-price-label", style={"fontWeight": "bold", "marginBottom": "0.5rem"}),
                html.Label("Last Price"),
                dcc.RangeSlider(float(df["last Price"].min()), float(df["last Price"].max()),
                    id="filter-last-price",
                    value=[float(df["last Price"].min()), float(df["last Price"].max()),],
                    allowCross=False,
                    step=1,
                    marks=None,
                    tooltip={
                        "placement": "bottom",
                        "always_visible": True,
                        "style": {"color": "white", "fontSize": "20px"},
                    },
                ),
            ])
        ], className="mb-4"),

        dbc.Button("Apply Filters", id="apply-filters-btn", color="primary", className="mb-3"),
    ]),

    # ── AG Grid to Display Filtered Results
    html.Div([
        dag.AgGrid(
            id="advanced-filter-grid",
            columnDefs=[
                {"field": "Ticker", "minWidth": 90, "maxWidth": 90},
                {"field": "Name", "minWidth": 240, "maxWidth": 300},
                {"field": "Sector", "minWidth": 200, "maxWidth": 300},
                {"field": "Industry", "minWidth": 250, "maxWidth": 320},
                {"field": "Avg Hold Period(days)", "minWidth": 140, "maxWidth": 180},
                {"field": "Volume Indicator", "minWidth": 130, "maxWidth": 150},
                {"field": "Beta Risk", "minWidth": 120, "maxWidth": 120},
                {"field": "last Price", "minWidth": 110, "maxWidth": 110},
                {"field": "Total Profit", "minWidth": 110, "maxWidth": 110}
            ],
            rowData=[],  # updated via callback
            columnSize="sizeToFit",
            style={"height": "600px", "width": "100%"},
        
            className="ag-theme-alpine"
        )
    ], style={"marginBottom": "1rem"})
])


Calculator = dbc.Card(
    dbc.CardBody([
        dbc.Row([
            # 🟥 Column 1 – Input Controls + Bottom Row
            dbc.Col(
                html.Div([
                    # Ticker Symbol Input
                    dbc.Row([
                        html.H4("Calculator", className="mb-4"),
                        dbc.Col([
                            html.Label('Ticker Symbol:', style={'textAlign': 'left', "width": "100%", 'paddingRight': '10px'})
                        ], width=4),
                        dbc.Col([
                            dcc.Input(id='ticker-input', type='text', placeholder="e.g. AAPL", className="form-control", style={"width": "60%", "maxWidth": "245px", "padding": "6px 12px", "border": "1px solid #ced4da", "borderRadius": "4px", "fontSize": "14px", "backgroundColor": "#fff"})
                        ], width=6)
                    ], style={'marginBottom': '10px'}),

                    # Initial Investment Input
                    dbc.Row([
                        dbc.Col([
                            html.Label('Investment:', style={'textAlign': 'left', 'paddingRight': '10px'})
                        ], width=4),
                        dbc.Col([
                            dcc.Input(id='investment-input', type='number', value=1000, className="form-control", style={"width": "60%", "maxWidth": "245px", "padding": "6px 12px", "border": "1px solid #ced4da", "borderRadius": "4px", "fontSize": "14px", "backgroundColor": "#fff"})
                        ], width=6)
                    ], style={'marginBottom': '10px'}),

                    # Mode Toggle + Input Group Row
                    dbc.Row([
                        # Left Column – Mode + Labels
                        dbc.Col([
                            dbc.RadioItems(
                                id="calc-mode",
                                options=[
                                    {"label": "Manual Entry", "value": "manual"},
                                    {"label": "Date Range", "value": "date"}
                                ],
                                value="manual",
                                labelStyle={"display": "block", "marginBottom": "30px"}
                            ),
                            html.Label("Platorm Fees:", style={"textAlign": "right", "paddingRight": "6px", "marginBottom": "20px"}),
                            html.Label("Trading Fees:", style={"textAlign": "right", "paddingRight": "6px", "marginBottom": "20px"}),
                            html.Label("Taxes (%):", style={"textAlign": "right", "paddingRight": "6px"})
                        ], width=4),

                        # Right Column – Inputs
                        dbc.Col([
                            dbc.Row([
                                dbc.Col([
                                    #dcc.Input(id="buy-price", type="number", placeholder="Buy Price", className="form-control", style={"width": "100%", "maxWidth": "280px", "marginBottom": "10px"})
                                    dcc.Input(id="buy-price", type="number", placeholder="Buy Price", className="form-control", style={"width": "110%", "maxWidth": "245px", "padding": "6px 12px", "border": "1px solid #ced4da", "borderRadius": "4px", "fontSize": "14px", "backgroundColor": "#fff", "marginBottom": "10px"})
                                ], width=6),
                                dbc.Col([
                                    #dcc.Input(id="sell-price", type="number", placeholder="Sell Price", className="form-control", style={"width": "100%", 'marginBottom': '10px'})
                                    dcc.Input(id="sell-price", type="number", placeholder="Sell Price", className="form-control", style={"width": "110%", "maxWidth": "245px", "padding": "6px 12px", "border": "1px solid #ced4da", "borderRadius": "4px", "fontSize": "14px", "backgroundColor": "#fff", "marginBottom": "10px"})
                                ], width=6)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dcc.DatePickerSingle(
                                        id="start-date",
                                        placeholder="Start date",
                                        display_format="DD/MM/YYYY",  # 👈 Custom date format
                                        style={"width": "95%", 'marginBottom': '10px'}
                                    )
                                ], width=6),
                                dbc.Col([
                                    dcc.DatePickerSingle(
                                        id="end-date",
                                        placeholder="End date",
                                        display_format="DD/MM/YYYY",  # 👈 Custom date format
                                        style={"width": "95%", 'marginBottom': '10px'}
                                    )
                                ], width=5)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dcc.Input(id="calc-platofrm-fees", type="number", value="11.99", className="form-control", style={"width": "110%", "maxWidth": "245px", "padding": "6px 12px", "border": "1px solid #ced4da", "borderRadius": "4px", "fontSize": "14px", "backgroundColor": "#fff", "marginBottom": "10px"}),
                                    dcc.Input(id="calc-trading-fees", type="number", value="3.99", className="form-control", style={"width": "110%", "maxWidth": "245px", "padding": "6px 12px", "border": "1px solid #ced4da", "borderRadius": "4px", "fontSize": "14px", "backgroundColor": "#fff", "marginBottom": "10px"}),
                                    dcc.Input(id="calc-taxes", type="number", value="0.005", className="form-control", style={"width": "110%", "maxWidth": "245px", "padding": "6px 12px", "border": "1px solid #ced4da", "borderRadius": "4px", "fontSize": "14px", "backgroundColor": "#fff", "marginBottom": "10px"})
                                ], width=6)
                            ]),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Reset", id="reset-btn", color="secondary", style={
                                    "width": "100%",
                                    "maxWidth": "120px",
                                    "marginRight": "10px"
                                    }),
                                ], width=6),
                                
                                dbc.Col([
                                    dbc.Button("Calculate", id="calculate-btn", color="primary", style={
                                        "width": "100%",
                                        "maxWidth": "120px"
                                    })
                                ], width=6)
                            ], style={"marginBottom": "20px"}),
                            
                            
                        ], width=7)
                    ], className="mb-2"),
                ]),
                width=4
            ),

            # 🟩 Column 2 – Green Placeholder
            dbc.Col([
                # Summary Card
                html.H4("Gain/ Loss", className="mb-4"),
                dbc.Card([
                    #dbc.CardHeader("*Disclaimer: Illustrative Gain/Loss", style={
                    #    "fontStyle": "italic",
                    #    "fontSize": "12px",
                    #    "color": "#6c757d",
                    #    "padding": "6px 10px",
                    #    "backgroundColor": "#f8f9fa"
                    #}),
                    html.Div("No Selection", id="company-name", style={
                        "fontWeight": "bold",
                        "fontSize": "18px",
                        "padding": "12px 10px",
                        "borderBottom": "1px solid #e2e2e2"
                    }),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div("Investment:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Div("Buy Price:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Div("Sell Price:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Div("Num Shares:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Hr(style={"margin": "8px 0", "border": "1px solid #0d6efd"}),
                                html.Div("Gross Gain Value:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Div("Platform Fees:", style={"fontWeight": "bold", "marginBottom": "10px"}), 
                                html.Div("Trading Fees:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Div("Taxes:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Hr(style={"margin": "8px 0", "border": "1px solid #0d6efd"}),
                                html.Div("Net Gain:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Div("Net Gain Value:", style={"fontWeight": "bold"})
                            ], width=6),
                            dbc.Col([
                                html.Div("0", id="cal-investment", style={"marginBottom": "10px"}),
                                html.Div("0", id="cal-buy-price", style={"marginBottom": "10px"}),
                                html.Div("0", id="cal-sell-price", style={"marginBottom": "10px"}),
                                html.Div("0", id="cal-num-shares", style={"marginBottom": "10px"}),
                                html.Hr(style={"margin": "8px 0", "border": "1px solid #0d6efd"}),
                                html.Div("0", id="gain-value", style={"marginBottom": "10px"}),
                                html.Div("0", id="platform-fees", style={"marginBottom": "10px"}),
                                html.Div("0", id="trading-fees", style={"marginBottom": "10px"}),
                                html.Div("0", id="taxes", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Hr(style={"margin": "8px 0", "border": "1px solid #0d6efd"}),
                                html.Div("0%", id="net-gain", style={"marginBottom": "10px"}),
                                html.Div("0", id="net-gain-value", style={"fontWeight": "bold"})
                            ], width=6)
                        ])
                    ]),
                    dbc.CardHeader("*Disclaimer: Illustrative Gain/Loss", style={
                        "fontStyle": "italic",
                        "fontSize": "12px",
                        "color": "#ffffff",
                        "padding": "6px 10px",
                        "backgroundColor": "#0d6efd"
                    }),                    
                ], style={
                    "backgroundColor": "#ffffff",
                    "padding": "0px",
                    "borderRadius": "8px",
                    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
                }),
                
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            dbc.DropdownMenu(
                                label="Calculation Used",
                                children=[
                                    dbc.DropdownMenuItem(
                                        html.Pre(
                                            "tax_amount = investment * taxes\n"
                                            "adjusted_investment = investment - tax_amount\n"
                                            "shares = adjusted_investment / buy\n"
                                            "gain = (shares * sell) - adjusted_investment\n"
                                            "total_trading_fees = trading_fees * 2\n"
                                            "num_months = end_date - start_date\n"
                                            "total_platform_fees = platform_fees * num_months\n"
                                            "net_gain_value = gain - total_trading_fees - total_platform_fees\n"
                                            "roi_percent = round((net_gain_value / investment) * 100, 2)\n"
                                            "\n"
                                            "* total_platform_fees are not applied in 'Manual Entry'",
                                            style={
                                                "whiteSpace": "pre-wrap",
                                                "fontSize": "0.85rem",
                                                "fontFamily": "Segoe UI, Open Sans, sans-serif",
                                                "margin": 0
                                            }
                                        ),
                                        disabled=True
                                    )
                                ],
                                color="secondary",
                                align_end=False,
                                style={"minWidth": "600px"}  # 👈 Stretch that width!
                            )
                        ]),
                        width="auto",
                        style={"marginTop": "8px"}
                    )
                ], style={"marginTop": "20px", "justifyContent": "left"})
            ], width=3),



            # 🟦 Column 3 – Blue Placeholder
            dbc.Col([
                html.H4("Performance Chart", className="mb-4"),

                dcc.Graph(
                    id="performance-graph",
                    style={"height": "465px", "border": "1px solid #D3D3D3"}  # You can tweak the height to suit your layout
                )
            ], width=5)

        ], className="g-3")
    ], style={
        "backgroundColor": "#f9f9f9",
        "padding": "20px",
        "borderRadius": "10px"
    }),
    className="mt-4"
)



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            
        ], width=2,  style={"paddingTop": "5px", "paddingLeft": "20px", "paddingBottom": "5px"}),

        dbc.Col([
            #html.H1("Stock Analyser", className="display-4",
            #    style={'color': 'white', 'font-style': 'italic', 'backgroundColor': 'grey'}),
        ], width=5),

        dbc.Col([
            dbc.Row(
                [
                    dbc.Col(
                        dbc.DropdownMenu(
                            label="Menu",
                            children=menuitems,
                            align_end=False,
                            color="secondary"
                        ), width="auto"
                    ),
                    dbc.Col(
                        dbc.Input(type="password", placeholder="Enter Token ID for pro version"),
                        className="me-3",
                    ),
                    dbc.Col(dbc.Button("Submit", color="secondary"), width="auto"),
                ], className="g-2", style={"paddingTop": "20px"}
            )
        ], width=5)
    ]),
    
    dbc.Col([
        dbc.Tabs([
                dbc.Tab(honepage_content, label="Home"),
                dbc.Tab(propage_content, label="Pro Analysis"),
                dbc.Tab(advanced_filter, label="Advanced Filter"),
                dbc.Tab(Calculator, label="Calculator"),
                
        ]),
   ]),

], fluid=True)


@app.callback(
    Output("sector-button-container", "children"),
    Input("selected-sector-store", "data")
)
def update_sector_buttons(selected_sector):
    return html.Div(
        dbc.ButtonGroup(
            [
                dbc.Button(
                    sector,
                    id={"type": "sector-btn", "index": sector},
                    color="primary" if sector == selected_sector else "secondary",
                    outline=not (sector == selected_sector),
                    active=sector == selected_sector
                )
                for sector in unique_sectors
            ],
            style={"overflowX": "auto", "whiteSpace": "nowrap"}
        ),
        style={"display": "flex", "justifyContent": "center"}
    )



@app.callback(
    Output("bar-graph", "figure"),
    Output("company_industry_list", "rowData"),
    Output("selected-sector-store", "data"),
    Input({'type': 'sector-btn', 'index': dash.ALL}, "n_clicks"),
    Input("bar-graph", "clickData"),
    State("selected-sector-store", "data")
)
def update_bar_and_table(n_clicks_list, click_data, stored_sector):
    trigger = ctx.triggered_id
    selected_sector = stored_sector

    if isinstance(trigger, dict) and trigger.get("type") == "sector-btn":
        selected_sector = trigger["index"]

    if not selected_sector:
        return dash.no_update, dash.no_update, dash.no_update

    # [rest of the filtering and plotting code]

    filtered_df = df[df["Sector"] == selected_sector]

    if click_data and click_data.get("points"):
        clicked_industry = click_data["points"][0]["x"]
        filtered_df = filtered_df[filtered_df["Industry"] == clicked_industry]

    industry_totals = df[df["Sector"] == selected_sector].groupby("Industry", dropna=False)["Total Profit"].sum().reset_index()

    fig = px.bar(
        industry_totals,
        x="Industry",
        y="Total Profit",
        title=f"Total Profit by Industry in {selected_sector}",
        labels={"Total Profit": "Total Profit (£)", "Industry": "Industry"},
        text_auto=".2s"
    )
    fig.update_traces(
        marker_color="#ebf5ff",
        marker_line=dict(width=1.2, color="#78afd9")
    )
    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(family="Segoe UI", size=14),
        margin=dict(t=60, l=40, r=20, b=40),
        title_font=dict(size=20, family="Segoe UI", color="#333"),
        xaxis=graph_properties,
        yaxis=graph_properties
    )

    return fig, filtered_df.to_dict("records"), selected_sector

def get_gauge_values(ticker):

    try:
        #df = pd.read_csv("BATCH.csv")
        df.columns = df.columns.str.strip()  # Clean headers
        row = df[df["Ticker"] == ticker]
        #print(f"get_gauge_values::{row}")

        if not row.empty:
            volume_raw = row["Volume Indicator"].values[0]
            beta_raw = row["Beta Risk"].values[0]

            # Handle 'UNKNOWN' cases
            volume = 0 if str(volume_raw).strip().upper() == "UNKNOWN" else float(volume_raw)
            beta = -5 if str(beta_raw).strip().upper() == "UNKNOWN" else float(beta_raw)
            
            # Clamp volume and beta just in case
            volume = max(0, min(volume, 10))
            beta = max(-5, min(beta, 5))

            
            return volume, beta

    except Exception as e:
        print(f"Gauge data error: {e}")

    # Fallback: volume = 0, beta = 5 (centered on gauge)
    return 0, 5
    
 
def get_buysell_signals(ticker):
    try:
        #df_buysell = pd.read_csv("BUYSELL.csv")
        #df_buysell = pd.read_csv("BUYSELL.csv", encoding='ISO-8859-1')  # or try cp1252

        filtered = df_buysell[df_buysell["Ticker"] == ticker].copy()

        if not filtered.empty:
            total_profit = filtered["Profit"].sum()
            summary_row = {
                "Profit": round(total_profit, 2), "is_summary": True  # new flag
            }
            filtered = pd.concat([filtered, pd.DataFrame([summary_row])], ignore_index=True)


        # Format or process columns if needed
        return filtered.to_dict("records")
    except Exception as e:
        print(f"Error loading BUYSELL.csv: {e}")
        return []
    
@app.callback(
    Output("line-graph", "figure"),
    Output("macd-graph", "figure"),
    Output("rsi-graph", "figure"),
    Output("ema-graph", "figure"),
    Output("buy-sell-table", "rowData"),
    Output("volume-gauge", "value"),
    Output("beta-gauge", "value"),
    Output("dynamic-tab", "label"),
    Input("company_industry_list", "selectedRows"),
    prevent_initial_call=True
)
def update_stock_chart(selected_rows):
    if selected_rows:
        ticker = selected_rows[0]['Ticker']
        selected_company = selected_rows[0]['Name']
        
        try:
            hist = yf.download(ticker, period="6mo", interval="1d", auto_adjust=False, progress=False)
            hist.reset_index(inplace=True)
            hist.columns = [col if isinstance(col, str) else col[0] for col in hist.columns]
            hist.rename(columns={"Date": "Datetime"}, inplace=True)

            if hist.empty:
                empty_fig = px.line(title=f"No data available for {ticker}")
                return empty_fig, empty_fig, empty_fig, empty_fig, [], 0, 0, "No Selection"

            # ── Line Chart
            min_close = hist['Close'].min()
            max_close = hist['Close'].max()
            buffer = (max_close - min_close) * 0.05
            y_range = [min_close - buffer, max_close + buffer]

            fig_line = px.line(hist, x="Datetime", y="Close")
            fig_line.update_traces(
                fill='tozeroy',
                fillcolor='rgba(214,235,255,0.5)',
                mode="lines",
                line=dict(color="#78afd9")
            )
            fig_line.update_layout(
                title=f"{ticker}: {selected_company}",
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
                font=dict(family="Segoe UI", size=14),
                margin=dict(t=60, l=40, r=20, b=40),
                xaxis=graph_properties,
                yaxis={**graph_properties, "range": y_range}
            )

            # ── EMA
            hist['EMA_10'] = hist['Close'].ewm(span=10, adjust=False).mean()
            hist['EMA_30'] = hist['Close'].ewm(span=30, adjust=False).mean()

            fig_ema = go.Figure([
                go.Scatter(x=hist['Datetime'], y=hist['Close'], mode='lines', name='Close Price',
                           line=dict(color="#78afd9"), fill='tozeroy', fillcolor='rgba(214,235,255,0.5)'),
                go.Scatter(x=hist['Datetime'], y=hist['EMA_10'], mode='lines', name='10-Day EMA',
                           line=dict(color='orange', dash='dot')),
                go.Scatter(x=hist['Datetime'], y=hist['EMA_30'], mode='lines', name='30-Day EMA',
                           line=dict(color='green', dash='dot'))
            ])
            fig_ema.update_layout(title=f"{ticker}: {selected_company}", plot_bgcolor='white', yaxis={**graph_properties, "range": y_range},
                    legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.2,
                    xanchor="right",
                    x=1
                )
            )
            fig_ema.update_xaxes(**graph_properties)

            # ── RSI
            delta = hist['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
            rs = gain / loss
            hist['RSI'] = 100 - (100 / (1 + rs))

            fig_rsi = go.Figure([
                go.Scatter(x=hist['Datetime'], y=hist['RSI'], mode='lines', name='RSI',
                           line=dict(color="#78afd9"), fill='tozeroy', fillcolor='rgba(214,235,255,0.5)'),
                go.Scatter(x=hist['Datetime'], y=[70]*len(hist), mode='lines', name='Overbought (70)',
                           line=dict(dash='dot', color='grey')),
                go.Scatter(x=hist['Datetime'], y=[30]*len(hist), mode='lines', name='Oversold (30)',
                           line=dict(dash='dot', color='green'))
            ])
            fig_rsi.update_layout(title=f"{ticker}: {selected_company}", plot_bgcolor='white',
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.2,
                    xanchor="right",
                    x=1
                )
            )
            fig_rsi.update_xaxes(**graph_properties)
            fig_rsi.update_yaxes(**graph_properties)

            # ── MACD
            exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
            exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
            hist['MACD'] = exp1 - exp2
            hist['Signal Line'] = hist['MACD'].ewm(span=9, adjust=False).mean()
            hist['MACD Histogram'] = hist['MACD'] - hist['Signal Line']

            # Smooth histogram using spline
            x = np.arange(len(hist))
            y = hist['MACD Histogram'].values
            spline = make_interp_spline(x, y, k=3)
            x_smooth = np.linspace(x.min(), x.max(), len(hist))
            y_smooth = spline(x_smooth)

            fig_macd = go.Figure([
                go.Scatter(x=hist['Datetime'], y=hist['MACD'], mode='lines', name='MACD',
                           line=dict(color='green')),
                go.Scatter(x=hist['Datetime'], y=hist['Signal Line'], mode='lines', name='Signal Line',
                           line=dict(color='grey', dash='dot')),
                go.Scatter(x=hist['Datetime'], y=y_smooth, mode='lines', name='Momentum',
                           fill='tozeroy', fillcolor='rgba(214,235,255,0.5)', line=dict(color="#78afd9"))
            ])

            fig_macd.update_layout(
                title=f"{ticker}: {selected_company}", plot_bgcolor='white',
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.2,
                    xanchor="right",
                    x=1
                )
            )

            fig_macd.update_xaxes(**graph_properties)
            fig_macd.update_yaxes(**graph_properties)

            signal_data = get_buysell_signals(ticker)
            
            volume_val, beta_val = get_gauge_values(ticker)

            
            return fig_line, fig_macd, fig_rsi, fig_ema, signal_data, volume_val, beta_val, selected_company


        except Exception as e:
            error_fig = px.line(title=f"Error: {e}")
            return error_fig, error_fig, error_fig, error_fig, [], 0, 0, "No Selection"
    
    return go.Figure(), go.Figure(), go.Figure(), go.Figure() , [], 0, 0, "No Selection"   

@app.callback(
    Output("advanced-filter-store", "data"),
    Input("apply-filters-btn", "n_clicks"),
    State("filter-sector", "value"),
    State("filter-industry", "value"),
    State("filter-hold-period", "value"),
    State("filter-volume", "value"),
    State("filter-beta", "value"),
    State("filter-last-price", "value"),  # ← Add this
    prevent_initial_call=True
)
def store_advanced_filter(n, sector, industry, hold, volume, beta, last_price):
    return {
        "sector": sector,
        "industry": industry,
        "hold_range": hold,
        "volume_range": volume,
        "beta_range": beta,
        "last_price_range": last_price
    }
    
@app.callback(
    Output("advanced-filter-grid", "rowData"),
    Input("advanced-filter-store", "data")
)
def update_advanced_filtered_table(filter_data):
    if not filter_data:
        return df.to_dict("records")

    filtered = df.copy()
    #print(df.columns.tolist())


    if filter_data.get("sector"):
        filtered = filtered[filtered["Sector"].isin(filter_data["sector"])]

    if filter_data.get("industry"):
        filtered = filtered[filtered["Industry"].isin(filter_data["industry"])]

    hold_min, hold_max = filter_data["hold_range"]
    filtered = filtered[
        (filtered["Avg Hold Period(days)"] >= hold_min) &
        (filtered["Avg Hold Period(days)"] <= hold_max)
    ]

    if "Volume Indicator" in filtered.columns:
        vol_min, vol_max = filter_data["volume_range"]
        filtered["Volume Indicator"] = pd.to_numeric(filtered["Volume Indicator"], errors="coerce")

        filtered = filtered[
            (filtered["Volume Indicator"] >= vol_min) &
            (filtered["Volume Indicator"] <= vol_max)
        ]

    if "Beta Risk" in filtered.columns:
        beta_min, beta_max = filter_data["beta_range"]
        filtered["Beta Risk"] = pd.to_numeric(filtered["Beta Risk"], errors="coerce")

        filtered = filtered[
            (filtered["Beta Risk"] >= beta_min) &
            (filtered["Beta Risk"] <= beta_max)
        ]
    
    if "last_price_range" in filter_data:
        price_min, price_max = filter_data["last_price_range"]
        filtered["last Price"] = pd.to_numeric(filtered["last Price"], errors="coerce")
        filtered = filtered[
            (filtered["last Price"] >= price_min) &
            (filtered["last Price"] <= price_max)
        ]


    return filtered.to_dict("records")

@app.callback(
    Output("last-price-label", "children"),
    Input("filter-last-price", "value")
)
def update_last_price_label(price_range):
    low, high = price_range
    return f"Selected Price Range: {low:,.2f} – {high:,.2f}"
    
@app.callback(
    Output("Beta-Risk-label", "children"),
    Input("filter-beta", "value")
)
def update_Beta_Risk_label(beta):
    low, high = beta
    return f"Selected Beta Range: {low:,.2f} – {high:,.2f}"
    

def get_company_info(stock_symbol):
    DEFAULT_UNKNOWN = "No Selection"
    
    # Initialize default values
    company_name_cleaned = DEFAULT_UNKNOWN
    
    # Using Yahoo Finance API URL is more reliable than info.get
    # But it can fail to get all the require data too :(
    yfinance_url = "https://query2.finance.yahoo.com/v1/finance/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }
    params = {"q": stock_symbol, "quotes_count": 1}

    try:
        response = requests.get(yfinance_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if data contains quotes
            if "quotes" in data and data["quotes"]:
                quote = data["quotes"][0]
                
                company_name_cleaned = re.sub(r',', ' ', quote.get('longname', DEFAULT_UNKNOWN))
                #sector_cleaned = re.sub(r',', ' ', quote.get('sector', DEFAULT_UNKNOWN))
                #industry_cleaned = re.sub(r'[,—]', ' ', quote.get('industry', DEFAULT_UNKNOWN))
                #sector_industry = f"{sector_cleaned}, {industry_cleaned}"

        else:
            print(f"yfinance_url: Error Received status code {response.status_code}")
    
    except Exception as e:
        print(f"yfinance_url: Error fetching company info for {stock_symbol}: {e}")
    
    return company_name_cleaned


    
@app.callback(
    Output("ticker-input", "value"),
    Output("investment-input", "value"),
    Output("buy-price", "value"),
    Output("sell-price", "value"),
    Output("start-date", "date"),
    Output("end-date", "date"),
    Output("calc-platofrm-fees", "value"),
    Output("calc-trading-fees", "value"),
    Output("calc-taxes", "value"),
    Input("reset-btn", "n_clicks")
)
def reset_inputs(n_clicks):
    if not n_clicks:
        raise PreventUpdate

    # 🎯 Return defaults (adjust values as needed)
    return "", 1000, 0, 0, None, None, 11.99, 3.99, 0.05


@app.callback(
    Output("net-gain", "children"),
    Output("gain-value", "children"),
    Output("platform-fees", "children"),
    Output("trading-fees", "children"),
    Output("taxes", "children"),
    Output("net-gain-value", "children"),
    Output("company-name", "children"),
    Output("performance-graph", "figure"),
    Output("cal-buy-price", "children"),
    Output("cal-sell-price", "children"),
    Output("cal-num-shares", "children"),
    Output("cal-investment", "children"),
    Input("calculate-btn", "n_clicks"),
    State("ticker-input", "value"),
    State("investment-input", "value"),
    State("calc-mode", "value"),
    State("buy-price", "value"),
    State("sell-price", "value"),
    State("start-date", "date"),
    State("end-date", "date"),
    State("calc-platofrm-fees", "value"),
    State("calc-trading-fees", "value"),
    State("calc-taxes", "value")
)
def calculate_metrics(n_clicks, ticker, investment, mode, buy, sell, start_date, end_date, platform_fees, trading_fees, taxes):
    #if not n_clicks:
    #    raise PreventUpdate

    # Convert values safely
    try:
        ticker = ticker.strip().upper()
        investment = float(investment) if investment else 0
        buy = float(buy) if buy else 0
        sell = float(sell) if sell else 0
        platform_fees = float(platform_fees) if platform_fees else 0
        total_platform_fees = platform_fees
        trading_fees = float(trading_fees) if trading_fees else 0
        taxes = float(taxes) if taxes else 0
        fig = go.Figure()
        calculated_buy_price = 0
        calculated_sell_price = 0
        calculated_num_shares = 0
        
        
    except Exception:
        return "0%", "0", "0", "0", "0", "0", "No Selection", go.Figure(), "0", "0", "0", "0"

    if not ticker or not isinstance(ticker, str) or not ticker.strip():
         return "0%", "0", "0", "0", "0", "0", "No Selection", go.Figure(), "0", "0", "0", "0"

    roi_percent, gain, net_gain_value, tax_amount = 0, 0, 0, 0

    if mode == "manual":
        #tax_amount = investment * taxes
        tax_amount = investment * taxes
        adjusted_investment = investment - tax_amount
        shares = adjusted_investment / buy if buy else 0
        gain = (shares * sell) - adjusted_investment
        total_trading_fees = trading_fees * 2
        net_gain_value = gain - total_trading_fees
        roi_percent = round((net_gain_value / investment) * 100, 2) if investment else 0
        total_platform_fees = 0
        data = yf.download(ticker, period="1y", auto_adjust=True)
        calculated_buy_price = buy
        calculated_sell_price = sell
        calculated_num_shares = shares
        

    elif mode == "date":
        if not all([ticker, start_date, end_date]):
            print(F"MODE ERROR: ticker:{ticker}, start_date{start_date}, end_date{end_date}")
            return "0%", "0", f"{platform_fees}", f"{trading_fees * 2}", "0", "0", "No Selection", go.Figure(), "0", "0", "0", "0"
            
        #check the dates are valid
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        
        if end_date_obj < start_date_obj:
            print("Date error:")
            return "0%", "0", f"{platform_fees}", f"{trading_fees * 2}", "0", "0", "No Selection", go.Figure(), "0", "0", "0", "0"

        try:
            # 🔍 Get historical data
            data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)

            if data.empty or "Close" not in data.columns:
                print(f"{data}")
                return "0%", "0", f"{platform_fees}", f"{trading_fees * 2}", "0", "0", "No Selection", go.Figure(), "0", "0", "0", "0"

            buy = float(data['Close'].iloc[0].item())     # ✅ Preferred
            sell = float(data['Close'].iloc[-1].item())   # ✅ Last row safely too

            # calculate number of monhs elasped
            num_months = int((end_date_obj.year - start_date_obj.year) * 12 + end_date_obj.month - start_date_obj.month)
            if num_months > 1:
                total_platform_fees = float(platform_fees * num_months)
            
            #print (F"num_months:{num_months}, platform_fees{platform_fees}, total_platform_fees{total_platform_fees}")
            
            tax_amount = investment * taxes
            adjusted_investment = investment - tax_amount
            shares = adjusted_investment / buy if buy else 0
            gain = (shares * sell) - adjusted_investment
            total_trading_fees = trading_fees * 2
            net_gain_value = gain - total_trading_fees - total_platform_fees
            roi_percent = round((net_gain_value / investment) * 100, 2) if investment else 0
            
            calculated_buy_price = buy
            calculated_sell_price = sell
            calculated_num_shares = shares

        except Exception:
            return "0%", "0", f"{total_platform_fees}", f"{trading_fees * 2}", "0", "0", "No Selection", go.Figure(), "0", "0", "0", "0"
        
        
    company_long_name = get_company_info(ticker)
    
    if not data.empty:
        
        # Access Close prices using the dynamic ticker
        
        close_series = data["Close"][ticker]

        # Build the figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=close_series.index,
            y=close_series.values,
            mode="lines",
            name=ticker.upper(),
            line=dict(color="#78afd9"),
            fill="tozeroy",
            fillcolor="rgba(214,235,255,0.5)")
        )
        fig.update_layout(
            title=dict(
                text=f"{ticker.upper()} : {company_long_name}",
                #font=dict(size=18, family="Arial", color="#000", weight="bold"),
                x=0.1,              # 👈 Position far left
                xanchor="left",     # 👈 Anchor text to the left edge
                y=0.955,              # Optional: lower it slightly
                yanchor="top"
            ),
            xaxis_title="Datetime",
            yaxis_title="Close Price",
            margin=dict(l=40, r=10, t=50, b=40),
            xaxis=graph_properties,
            yaxis=graph_properties,
            plot_bgcolor="#ffffff"
        )

        #fig.update_layout(
        #    title=f"{ticker.upper()}:{company_long_name}",
        #    xaxis_title="Datetime",
        #    yaxis_title="Close Price",
        #    margin=dict(l=40, r=10, t=40, b=40),
        #    xaxis=graph_properties,
        #    yaxis=graph_properties,
        #    plot_bgcolor="#ffffff",
        #)


    return (
        f"{roi_percent}%",
        f"{round(gain+tax_amount, 2)}",
        f"{round(total_platform_fees, 2)}",
        f"{round(trading_fees * 2, 2)}",
        f"{round(tax_amount, 2)}",
        f"{round(net_gain_value, 2)}",
        f"{company_long_name}",
        fig,
        f"{round(calculated_buy_price,6)}",
        f"{round(calculated_sell_price,6)}",
        f"{int(calculated_num_shares)}",
        f"{investment}"
        
    )




if __name__ == "__main__":
    app.run(debug=True)