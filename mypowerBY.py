import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, ctx
import dash_ag_grid as dag
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from scipy.interpolate import make_interp_spline
import dash_daq as daq
import requests
import re

from dash.dcc import Download, send_file
import os

from dash.exceptions import PreventUpdate
from datetime import datetime
import tzlocal
import json

from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo

# ---------------------------------------------------
# FTSE Sectors 
# ---------------------------------------------------
uk_sector_indices = {
    "Industrials": ["AVON.L","BA.L","BAB.L","BBY.L","BOY.L", 
    "CHG.L","CKN.L","COST.L","CWR.L","EAAS.L","EXPN.L","EZJ.L","FAN.L",
    "FGP.L","GEN.L","GFRD.L","GFTU.L","HAS.L","HILS.L","HLMA.L","IAG.L",
    "IMI.L","ITRK.L","JSG.L","KIE.L","KLR.L","MEGP.L","MGAM.L","MGNS.L",
    "MRO.L","MTO.L","PAGE.L","QQ.L","REL.L","RHIM.L","ROR.L","RR.L",
    "RS1.L","RTO.L","SMIN.L","SNR.L","SRP.L","STEM.L","TPK.L","WATR.L",
    "WEIR.L","WIZZ.L","ZIG.L"],
    #"BMTO.L"],
    
    "Financial Services": [
    "ABDN.L","ADM.L","AJB.L","ASHM.L","BARC.L","BEZ.L","BPT.L","CABP.L",
    "CAV.L","CBG.L","CMCX.L","CSN.L","DFCH.L","EMG.L","FCH.L","FSG.L",
    "HSBA.L","HSX.L","IHP.L","IGG.L","INVP.L","IPF.L","IPO.L","JUP.L",
    "JUST.L","LGEN.L","LLOY.L","LRE.L","MNG.L","MTRO.L","N91.L","OSB.L",
    "PAG.L","PLUS.L","POLN.L","PPH.L","PRU.L","QLT.L","RAT.L","SHAW.L",
    "STAN.L","STJ.L","TBCG.L","TCAP.L"],

    "Basic Materials": [
    "1SN.L","AAL.L","ANTO.L","ATYM.L","BREE.L","CAML.L","EDV.L","ELM.L",
    "FRES.L","GLEN.L","HOC.L","IBST.L","JMAT.L","KAV.L","MNDI.L","MSLH.L",
    "ORR.L","PAF.L","SAV.L","VCT.L","VSVS.L"],

    "Consumer Cyclical": [
    "AML.L","ANG.L","AO.L","AURR.L","AUTG.L","BKG.L","BOWL.L","BRBY.L",
    "BTRW.L","BWY.L","CCL.L","COA.L","CPG.L","CURY.L","DNLM.L","DOCS.L",
    "DOM.L","ENT.L","FRAS.L","GRG.L","HWDN.L","IHG.L","INCH.L","JD.L",
    "JDW.L","KGF.L","MAB.L","MKS.L","MOON.L","PETS.L","PPH.L","PSN.L",
    "PTEC.L","RNK.L","SMWH.L","SSPG.L","TENG.L","THG.L","TRN.L","TW.L",
    "VTY.L","WIX.L","WOSG.L","WTB.L","XPS.L"],

    "Consumer Defensive": [
    "ABF.L","AEP.L","APN.L","BAG.L","BATS.L","BME.L","BNZL.L","CCH.L",
    "CCR.L","DGE.L","GNC.L","HFG.L","IMB.L","OCDO.L","PFD.L","PRN.L",
    "SBRY.L","TATE.L","TSCO.L"],

    "Communication Services": [
    "AAF.L","AUTO.L","BBSN.L","BCG.L","FOUR.L","FUTR.L","GAMA.L",
    "HTWS.L","INF.L","ITV.L","MONY.L","PSON.L","RMV.L","VOD.L","WPP.L"],

    "Energy": [
    "BP.L","DCC.L","ENOG.L","HBR.L","HTG.L","ITH.L","SHEL.L"],

    "Healthcare": [
    "AVCT.L","CTEC.L","GNS.L","GSK.L","HIK.L","HLN.L","ONT.L",
    "OXB.L","SPI.L","SN.L"],

    "Real Estate": [
    "BLND.L","BYG.L","DLN.L","GPE.L","GRI.L","HMSO.L","HWG.L",
    "IWG.L","LAND.L","LMP.L","NRR.L","PHP.L","SAFE.L","SHC.L",
    "SRE.L","SVS.L","UTG.L","WKP.L"],

    "Technology": [
    "ALFA.L","BYIT.L","CCC.L","DSCV.L","EWG.L","GBG.L","ING.L",
    "KNOS.L","NCC.L","OXIG.L","PCT.L","PINE.L","RPI.L","RSW.L",
    "SAAS.L","SCT.L","SGE.L","TRST.L"],

    "Utilities": [
    "CNA.L","DRX.L","HGEN.L","MTLN.L","NG.L","PNN.L","SSE.L",
    "TEP.L","TRIG.L","UKW.L","UU.L"],
}

# ---------------------------------------------------
# Sector ETF symbols (S&P 500 sectors)
# ---------------------------------------------------
us_sector_indices = {
    "Materials (XLB)": "XLB",
    "Energy (XLE)": "XLE",
    "Financials (XLF)": "XLF",
    "Industrials (XLI)": "XLI",
    "Technology (XLK)": "XLK",
    "Consumer Staples (XLP)": "XLP",
    "Utilities (XLU)": "XLU",
    "Health Care (XLV)": "XLV",
    "Consumer Discretionary (XLY)": "XLY",
    "Real Estate (XLRE)": "XLRE",
    "Communication Services (XLC)": "XLC"
}

metals_indices = {
    "Gold": ["GC=F"],
    "Silver": ["SI=F"],
    "Platinum": ["PL=F"],
    "Palladium": ["PA=F"],
    "Copper": ["HG=F"]
}

crypto_indices = {
    "Bitcoin": ["BTC-USD"],
    "Ethereum": ["ETH-USD"],
    "Solana": ["SOL-USD"],
    "Binance Coin": ["BNB-USD"],
    "XRP": ["XRP-USD"]
}


# Load data
DATA_ROOT = "data/Exchange"
country = "UK"
data_path = os.path.join(DATA_ROOT, country)

df = pd.read_csv(os.path.join(data_path, "BATCH.csv"), encoding='ISO-8859-1')  # or use 'cp1252'
#df_buysell = pd.read_csv(os.path.join(data_path, "BUYSELL.csv"), encoding='ISO-8859-1')  # or use 'cp1252'
#treemap_df_batch = df
#treemap_df_batch.columns = [col.strip() for col in treemap_df_batch.columns]
treemap_sector_options = sorted(df["Sector"].dropna().unique())


graph_properties = {
    'mirror': True,
    'ticks': 'outside',
    'showline': True,
    'linecolor': 'lightgrey',
    'gridcolor': 'lightgrey'
}

news_columnDefs = [
    {"field": "Date", "minWidth": 150, "maxWidth": 150, "sort": "desc"},
    {"field": "Ticker", "minWidth": 120, "maxWidth": 120},
    {"field": "link", "headerName": "Title", "linkTarget": "_blank", "minWidth": 900},
    {"field": "publisher", "minWidth": 150},
]

uk_stock_data = yf.download("^FTSE", period="1y", interval="1wk", auto_adjust=True) 
us_stock_data = yf.download("^GSPC", period="1y", interval="1wk", auto_adjust=True)



def build_sector_indices(sectors_indices):
    local_sector_data = {}
    
    for sector_name, tickers in sectors_indices.items():
        print (f"{sector_name}:  {tickers}")
        # Try downloading — allow partial success
        df = yf.download(tickers, period="1y", auto_adjust=True, progress=True)

        if df.empty:
            print(f"⚠ No data for sector: {sector_name}")
            continue

        # Flatten MultiIndex if needed
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() for col in df.columns]

        # Extract Close_ columns
        close_cols = [c for c in df.columns if c.startswith("Close_")]

        if not close_cols:
            print(f"⚠ No close prices for sector: {sector_name}")
            continue

        closes = df[close_cols].dropna(how="all")  # drop rows where ALL tickers are NaN

        if closes.empty:
            print(f"⚠ All tickers failed for sector: {sector_name}")
            continue

        # Remove tickers that failed entirely
        closes = closes.dropna(axis=1, how="all")

        if closes.empty:
            print(f"⚠ No usable tickers left in sector: {sector_name}")
            continue

        # Normalize
        closes.columns = [c.replace("Close_", "") for c in closes.columns]

        # Ensure at least 1 row remains
        if len(closes) < 2:
            print(f"⚠ Not enough data for sector: {sector_name}")
            continue

        norm = closes / closes.iloc[0] * 100.0
        sector_index = norm.mean(axis=1)

        sdf = pd.DataFrame({"Close": sector_index})
        sdf.index = sdf.index.tz_localize(None)

        sdf["DPCM_raw"] = sdf["Close"].diff()
        sdf["DPCM_q"] = sdf["DPCM_raw"].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

        local_sector_data[sector_name] = sdf
        
    return local_sector_data


def get_index_map():
    #Usage
    #index_map = get_index_map()
    #index_ticker = index_map[country]["ticker"]
    #index_label  = index_map[country]["label"]

    return {
        "UK": {"ticker": "^FTSE", "label": "FTSE 100", "data": uk_stock_data},
        "US": {"ticker": "^GSPC", "label": "S&P 500", "data": us_stock_data}
    }


def load_country_data(country):
    data_path = os.path.join(DATA_ROOT, country)

    df = pd.read_csv(os.path.join(data_path, "BATCH.csv"), encoding='ISO-8859-1')
    df_buysell = pd.read_csv(os.path.join(data_path, "BUYSELL.csv"), encoding='ISO-8859-1')
    past_df = pd.read_csv(os.path.join(data_path, "PAST.csv"), header=None)
    
    filenames = past_df.iloc[:, 0].tolist()
    values = past_df.iloc[:, 1].tolist()
    target_len = 52
    padded_values = [0] * (target_len - len(values)) + values[-target_len:]
    padded_filenames = [None] * (target_len - len(filenames)) + filenames[-target_len:]
    
    # Tree Map Data
    df_batch = df
    df_batch = df_batch.dropna(subset=["Ticker", "Sector", "Industry"])
    sector_options = sorted(df_batch["Sector"].dropna().unique())
            
    return df, df_buysell, padded_filenames, padded_values, sector_options
        

def create_figure(padded_values, country):
    index_map = get_index_map()
    index_label  = index_map[country]["label"]
    index_ticker = index_map[country]["ticker"]
    
    stock_data = index_map[country]["data"]
    
    #stock_data = yf.download(index_ticker, period="1y", interval="1wk", auto_adjust=True)

    #stock_data = yf.download('^FTSE', period="1y", interval='1wk', auto_adjust=True)
    stock_close = stock_data['Adj Close'].reset_index() if 'Adj Close' in stock_data.columns else stock_data['Close'].reset_index()
    dates = stock_close['Date'].tolist()
    
    # FTSE line trace with styling
    stock_trace = go.Scatter(
        x=dates,
        y=stock_close.iloc[:, 1],
        mode='lines',
        name=index_label,
        yaxis='y1',
        fill='tozeroy',
        fillcolor='rgba(214,235,255,0.5)',
        line=dict(color='#78afd9')
    )

    # Profit bar trace
    profit_trace = go.Bar(
        x=dates,
        y=padded_values,
        name='stockDash Profit',
        opacity=0.6,
        yaxis='y2',
        marker=dict(color='rgba(88,130,193,0.7)')  # translucent blue
    )

    # Determine FTSE y-axis range
    stock_range = [
        stock_close.iloc[:, 1].min() * 0.95,
        stock_close.iloc[:, 1].max() * 1.05
    ]

    # Layout with custom appearance
    layout = go.Layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(family="Segoe UI", size=14),
        margin=dict(t=90, l=100, r=100, b=40),
        xaxis=graph_properties,
        yaxis=dict(
            title=index_label,
            side='left',
            **graph_properties,
            range=stock_range
        ),
        yaxis2=dict(
            title='stockDash Profit',
            side='right',
            overlaying='y',
            showgrid=False,
            range=[
                min(padded_values) * 0.9,
                max(padded_values) * 1.1
            ],
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.2,
            xanchor="right",
            x=1
        )
    )
    
    return {'data': [stock_trace, profit_trace], 'layout': layout}


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
                html.H6(f"{profit:,.2f}", className="card-subtitle text-success mb-0")
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
        
        html.H4(f"Total Profit: {total_profit_all:,.2f}", className="text-primary mb-4"),
        html.H5("Sector Overview", className="mb-3"),
        dbc.Row(sector_cards, className="gx-3", align="stretch")
    ]),
    className="mb-4",
    style={"backgroundColor": "#f8f9fa"}
)

sector_data = {}
uk_sector_indices_data = build_sector_indices(uk_sector_indices)
us_sector_indices_data = build_sector_indices(us_sector_indices)
metals_indices_data = build_sector_indices(metals_indices)
crypto_indices_data = build_sector_indices(crypto_indices)

sector_data = uk_sector_indices_data

# Insert into your homepage_content layout
homepage_content = dbc.Card(
    dbc.CardBody([
        html.Div(
            style={
                'background-image': 'url("/assets/wwwhirl.svg")',
                'background-size': '1000px auto',
                'background-repeat': 'no-repeat',
                'height': '150vh',
                'display': 'flex',
                'flexDirection': 'column',
                'color': 'black',
                'font-size': '16px',
                'padding': '20px'
            },
            children=[
                dbc.Col([
                
                    dcc.Dropdown(
                        id="country-selector",
                        options=[
                            {"label": "United Kingdom", "value": "UK"},
                            {"label": "United States", "value": "US"}
                        ],
                        value="UK",
                        clearable=False,
                        style={"width": "250px", "marginBottom": "20px"}
                    ),
                    dcc.Store(id="country-store", data="UK"),
                    dcc.Store(id="store-df-batch"),
                    dcc.Store(id="store-df-buysell"),
                    dcc.Store(id="store-padded-filenames"),
                    dcc.Store(id="store-padded-values"),
                    dcc.Store(id="store-sector-options"),
                    
                    #dbc.Row(sector_summary_card, className="gx-3", align="stretch"),
                    html.Div(id="sector-summary-container"),

                    
                    dbc.Col([
                        dcc.Loading(
                            id="exchange-table",
                            type="default",
                            children=[
                                dcc.Graph(
                                    id='exchange-chart',
                                    style={"border": "1px solid #D3D3D3"}
                                )
                            ]
                        ),

                        html.Div([
                            dbc.Row([
                                dbc.Col(
                                    dcc.Input(
                                        id='filename-box',
                                        type='text',
                                        placeholder='Select Column',
                                        value='',
                                        readOnly=True,
                                        className="form-control",
                                        style={'width': '140px', 'marginBottom': '15px'}
                                    ),
                                    width="auto"
                                ),
                                dbc.Col(
                                    dbc.Button("Download", id="download-btn", color="primary", className="mb-3"),
                                    width="auto"
                                ),
                                Download(id='download')
                            ], align="center", justify="start")
                        ], style={'marginTop': '20px'})
                    ]),

                    html.Br(),
                    html.P(
                        "Stock Dash takes the output of a proprietary, in-house developed algorithm, "
                        "designed to pinpoint precise BUY and SELL signals for each stock listed in the selected Country Stock Exchange."
                    ),
                    html.Br()
                ], width=12)
            ]
        )
    ]),
    className="mt-3"
)

# Insert into your homepage_content layout
treemap_content = dbc.Card(
    dbc.CardBody([
        html.Div(
            children=[
                dbc.Col([
                    html.H4("Market Cap Treemap", style={"marginBottom": "10px"}),

                    html.Div([
                        dcc.Dropdown(
                            id="treemap_sector-dropdown",
                            options=[{"label": s, "value": s} for s in treemap_sector_options],
                            placeholder="All Sectors",
                            clearable=False,
                            style={"width": "250px", "marginBottom": "20px"}
                        ),
                        dcc.Dropdown(
                            id="treemap_industry-dropdown",
                            placeholder="All Industries",
                            clearable=False,
                            style={"width": "340px", "marginBottom": "20px"}
                        ),
                        dbc.Col(
                            dbc.Button("Generate", id="treemap_submit-button", color="primary", disabled=False),
                            width="auto"
                        ),

                    ], style={"display": "flex", "gap": "15px", "flexWrap": "wrap"}),

                    dcc.Store(id="stored-data"),

                    html.Div([
                        dcc.Loading(
                            id="loading-treemap",
                            type="default",
                            children=[
                                dcc.Graph(id="treemap-output", style={"height": "800px", "border": "1px solid #D3D3D3"})
                            ]
                        )
                    ], style={"marginTop": "-30px"})
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
            data=None
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
                        {"field": "Avg Hold Period(days)", "headerClass": "wrap-header", "minWidth": 120, "maxWidth": 120},
                        {"field": "BUY Range", "minWidth": 150, "maxWidth": 150},
                        {"field": "SELL Range", "minWidth": 150, "maxWidth": 150},
                        {"field": "Price Movement", "minWidth": 150, "maxWidth": 150},
                        {"field": "Dropped Samples %", "headerClass": "wrap-header", "minWidth": 110, "maxWidth": 110},
                        {"field": "Ask-Bid Spread", "headerClass": "wrap-header", "minWidth": 110, "maxWidth": 110},
                        {"field": "Total Profit", "minWidth": 110, "maxWidth": 110}
                    ],
                    rowData=df.to_dict("records"),
                    columnSize="sizeToFit",
                    dashGridOptions={"rowSelection": "single"},
                    style={"height": "400px",
                            "maxWidth": "1400px",     # 👈 controls grid width
                            "margin": "0 auto"
                          },
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
                                                            dbc.Row([
                                                                dbc.Col([
                                                                    html.H5("52w Low", style={"textAlign": "center", "fontSize": "10px"}),
                                                                    html.Div(id="52weeklow-price", children="0.00", style={"fontSize": "20px", "textAlign": "center"})
                                                                ]),  # Left spacer

                                                                dbc.Col([
                                                                    html.H5("Current Price", style={"textAlign": "center", "fontSize": "10px"}),
                                                                    html.Div(id="current-price", children="0.00", style={"fontSize": "24px", "textAlign": "center"})
                                                                ]),

                                                                dbc.Col([
                                                                    html.H5("52w High", style={"textAlign": "center", "fontSize": "10px"}),
                                                                    html.Div(id="52weekhigh-price", children="0.00", style={"fontSize": "20px", "textAlign": "center"})
                                                                ])  # Right spacer
                                                            ], style={"paddingTop": "5px", "paddingBottom": "20px"}),

                                                            dbc.Col([
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
                                                                ),
                                                                html.Div(
                                                                    id="volume-raw",
                                                                    children="0.00",
                                                                    style={"fontSize": "10px", "textAlign": "center", "marginTop": "-10px"}
                                                                )
                                                            ], width="auto", style={"textAlign": "center"}),

                                                            dbc.Col([
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
                                                                ),
                                                                html.Div(
                                                                    id="beta-raw",
                                                                    children="UNKNOWN",
                                                                    style={"fontSize": "10px", "textAlign": "center", "marginTop": "-10px"}
                                                                )
                                                            ], width="auto", style={"textAlign": "center"})

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
                                ),
                                
                                dbc.Tab(
                                    label="News Articles",
                                    children=[
                                        dcc.Loading(
                                            children=[
                                                dag.AgGrid(
                                                    id="news_articles",
                                                    columnSize="sizeToFit",
                                                    columnDefs=news_columnDefs,
                                                    defaultColDef={"cellRenderer": "markdown"},
                                                    rowData=[],
                                                    dangerously_allow_code=True
                                                ),
                                            ]
                                        ),
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
    style={"backgroundColor": "#f8f9fa", "marginTop": "20px"},
    
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
                    placeholder="All Sectors"
                )
            ], width=12, md=6),
            dbc.Col([
                html.Label("Industry"),
                dcc.Dropdown(
                    id="filter-industry",
                    options=[{"label": i, "value": i} for i in sorted(df["Industry"].dropna().unique())],
                    multi=True,
                    placeholder="All Industries"
                )
            ], width=12, md=6)
        ], className="mb-3", style={"marginTop": "1.5rem"}),

        # ── Risk Card
        dbc.Card([
            dbc.CardHeader("Risk Filter", style={"fontWeight": "bold", "fontSize": "0.8rem"}),

            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                    
                        html.Div([
                            html.Div("High Risk", style={
                                "display": "inline-block",
                                "width": "50%",
                                "textAlign": "left",
                                "fontWeight": "bold",
                                "marginBottom": "0.5rem"
                            }),
                            html.Div("Low Risk", style={
                                "display": "inline-block",
                                "width": "50%",
                                "textAlign": "right",
                                "fontWeight": "bold",
                                "marginBottom": "0.5rem"
                            })
                        ]),
                        
                        html.Label("Volume Indicator"),
                        dcc.RangeSlider(
                            id="filter-volume",
                            min=0, max=10,
                            value=[0, 10],
                            step=1,
                            allowCross=False,
                        )
                    ], width=12, md=4),

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
                    ], width=12, md=4),

                    dbc.Col([
                    
                        html.Div([
                            html.Div("Low Risk", style={
                                "display": "inline-block",
                                "width": "50%",
                                "textAlign": "left",
                                "fontWeight": "bold",
                                "marginBottom": "0.5rem"
                            }),
                            html.Div("High Risk", style={
                                "display": "inline-block",
                                "width": "50%",
                                "textAlign": "right",
                                "fontWeight": "bold",
                                "marginBottom": "0.5rem"
                            })
                        ]),
                    
                        html.Label("Dropped Samples %"),
                        dcc.RangeSlider(
                            id="filter-drop-samples",
                            min=int(df["Dropped Samples %"].min()),
                            max=int(df["Dropped Samples %"].max()),
                            value=[0, 60],
                            marks=None,
                            allowCross=False,
                            step=1,
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=12, md=4)
                ])
            ])
        ], className="mb-2", style={"padding": "0.0rem", "borderRadius": "0.5rem", "boxShadow": "0 0 4px rgba(0,0,0,0.1)"}),

        # ── Performance Card
        dbc.Card([
            dbc.CardHeader("Additional Filter", style={"fontWeight": "bold", "fontSize": "0.8rem"}),

            dbc.CardBody([
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
                            allowCross=False,
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=12, md=4, style={"marginTop": "0rem"}),

                    dbc.Col([
                        html.Label("Num of Trades (BUY/SELL Pairs)"),
                        dcc.RangeSlider(
                            id="filter-transactions",
                            min=int(df["Num of Trades"].min()),
                            max=int(df["Num of Trades"].max()),
                            value=[
                                int(df["Num of Trades"].min()),
                                int(df["Num of Trades"].max())
                            ],
                            marks=None,
                            allowCross=False,
                            step=1,
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=12, md=4, style={"marginTop": "0rem"}),

                    dbc.Col([

                        html.Label("Spread (ASK/BID price)"),
                        dcc.RangeSlider(
                            id="filter-ask-bid-spread",
                            min=int(df["Ask-Bid Spread"].min()),
                            max=int(df["Ask-Bid Spread"].max()),
                            value=[0, 4],
                            step=0.01,
                           
                            marks=None,
                            allowCross=False,
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=12, md=4, style={"marginTop": "0rem"}),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Hr(style={"marginTop": "1rem", "marginBottom": "1rem"}),
                        ]),
                        
                        html.Div(id="last-price-label", style={"fontWeight": "bold", "marginBottom": "0.5rem"}),
                        html.Label("Last Price"),
                        dcc.RangeSlider(
                            id="filter-last-price",
                            min=float(df["last Price"].min()),
                            max=float(df["last Price"].max()),
                            value=[float(df["last Price"].min()), float(df["last Price"].max())],
                            allowCross=False,
                            step=1,
                            marks=None,
                            tooltip={
                                "placement": "bottom",
                                "always_visible": True,
                                #"style": {"color": "white", "fontSize": "20px"},
                            },
                        ),
                    ]),

                ])
            ])
        ], className="mb-2", style={"padding": "0.0rem", "borderRadius": "0.5rem", "boxShadow": "0 0 4px rgba(0,0,0,0.1)"}),

        # ── Apply Button
        dbc.Button("Apply Filters", id="apply-filters-btn", color="primary", className="mb-3"),
    ]),

    # ── AG Grid to Display Filtered Results
    html.Div([
        dag.AgGrid(
            id="advanced-filter-grid",
            columnDefs=[
                {"field": "Ticker", "minWidth": 90, "maxWidth": 90},
                {"field": "Name", "minWidth": 230, "maxWidth": 300},
                {"field": "Sector", "minWidth": 170, "maxWidth": 300},
                {"field": "Industry", "minWidth": 220, "maxWidth": 320},
                {"field": "Avg Hold Period(days)", "headerClass": "wrap-header", "minWidth": 120, "maxWidth": 120},
                {"field": "Volume Indicator", "headerClass": "wrap-header", "minWidth": 100, "maxWidth": 100},
                {"field": "Num of Trades", "headerClass": "wrap-header", "minWidth": 90, "maxWidth": 90},
                {"field": "Beta Risk", "headerClass": "wrap-header", "minWidth": 90, "maxWidth": 110},
                {"field": "Dropped Samples %", "headerClass": "wrap-header", "minWidth": 110, "maxWidth": 110},
                {"field": "Ask-Bid Spread", "headerClass": "wrap-header", "minWidth": 110, "maxWidth": 110},
                {"field": "last Price", "minWidth": 100, "maxWidth": 100},
                {"field": "Total Profit", "minWidth": 110, "maxWidth": 110}
            ],
            rowData=[],  # updated via callback
            columnSize="sizeToFit",
            style={"height": "600px", "width": "100%"},
            className="ag-theme-alpine"
        )
    ], style={
        "maxWidth": "1500px",     # 👈 controls grid width
        "margin": "0 auto", 
        "marginBottom": "1rem"
       })
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
                            dbc.Col(html.Label("Platorm Fees:", style={"textAlign": "right", "paddingRight": "6px", "marginBottom": "20px"}), width=12),
                            dbc.Col(html.Label("Trading Fees:", style={"textAlign": "right", "paddingRight": "6px", "marginBottom": "20px"}), width=12),
                            dbc.Col(html.Label("Taxes (%):", style={"textAlign": "right", "paddingRight": "6px", "marginBottom": "20px"}), width=12),
                            dbc.Col(html.Label("Desired Profit:", style={"textAlign": "right", "paddingRight": "6px"}), width=12),
                            dbc.Col(html.Label("(Optional):", style={"textAlign": "right", "paddingRight": "6px"}), width=12)
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
                                    dcc.Input(id="calc-taxes", type="number", value="0.005", className="form-control", style={"width": "110%", "maxWidth": "245px", "padding": "6px 12px", "border": "1px solid #ced4da", "borderRadius": "4px", "fontSize": "14px", "backgroundColor": "#fff", "marginBottom": "10px"}),
                                    dcc.Input(id="desired-profit", type="number", value="50", className="form-control", style={"width": "110%", "maxWidth": "245px", "padding": "6px 12px", "border": "1px solid #ced4da", "borderRadius": "4px", "fontSize": "14px", "backgroundColor": "#fff", "marginBottom": "10px"})
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
                    html.Div("No Selection", id="company-name", style={
                        "fontWeight": "bold",
                        "fontSize": "18px",
                        "padding": "12px 10px",
                        "borderBottom": "1px solid #e2e2e2"
                    }),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div("Actual Investment:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Div("Buy Price:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Div("Sell Price:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Div("Num Shares:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Hr(style={"margin": "8px 0", "border": "1px solid #0d6efd"}),
                                html.Div("Gross Gain Value:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                                html.Div("Platform Fees:", style={"fontWeight": "bold", "marginBottom": "10px"}), 
                                html.Div("Trading Fees (x2):", style={"fontWeight": "bold", "marginBottom": "10px"}),
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
                                            
                                            "available_after_fee = investment - trading_fees\n"
                                            "share_cost_before_tax = available_after_fee / (1 + taxes)\n"
                                            "shares = int(share_cost_before_tax / buy)\n" 
                                            "actual_share_cost = shares * buy\n" 
                                            "stamp_duty = actual_share_cost * taxes\n" 
                                            "total_buy_cost = actual_share_cost + stamp_duty + trading_fees\n" 
                                            "sell_value = shares * sell\n" 
                                            "net_gain_value = sell_value - total_buy_cost - trading_fees - total_platform_fees\n"  
                                            "gain = sell_value - actual_share_cost\n" 
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
                html.H4("Desired Profit Graphical Calculator", className="mb-4"),
                dcc.Graph(
                    id="graphical-calculator-graph", style={"height": "465px", "border": "1px solid #D3D3D3"}  # You can tweak the height to suit your layout
                )
            ], width=5)

        ], className="g-3"),
        
        html.Hr(style={"borderTop": "2px solid #ccc"}),
        
        
        dbc.Row([
            dbc.Col([
                html.H4("Performance Charts", className="mb-4"),

                dbc.Tabs(
                    [
                        dbc.Tab(
                            dcc.Graph(
                                id="calculator-macd-performance-graph",
                                style={"height": "465px", "border": "1px solid #D3D3D3"}
                            ),
                            label="MACD"
                        ),
                        dbc.Tab(
                            dcc.Graph(
                                id="calculator-rsi-performance-graph",
                                style={"height": "465px", "border": "1px solid #D3D3D3"}
                            ),
                            label="RSI"
                        ),
                        dbc.Tab(
                            dcc.Graph(
                                id="calculator-ema-performance-graph",
                                style={"height": "465px", "border": "1px solid #D3D3D3"}
                            ),
                            label="EMA"
                        ),
                    ],
                    id="performance-tabs",
                    active_tab="calculator-performance-ema"   # default tab
                )
            ])
        ])

        
        
        
        #dbc.Row([
        #    dbc.Col([
        #        
        #        html.H4("Performance Chart", className="mb-4"),
        #        dcc.Graph(
        #            id="performance-graph",
        #            style={"height": "465px", "border": "1px solid #D3D3D3"}  # You can tweak the height to suit your layout
        #        )
        #    ])
        #])
        
    ], style={
        "backgroundColor": "#f9f9f9",
        "padding": "20px",
        "borderRadius": "10px",
        "marginTop": "-10px",
        "height": "1200px"
    }),
    className="mt-4"

)

# Insert into your sector_indicies_content layout
sector_indicies_content = dbc.Card(
    dbc.CardBody([

        html.H4("Global Sector Indices Analysis"),

        # -----------------------------
        # Ranking strip
        # -----------------------------
        html.Div(id="ranking-panel", style={"margin-bottom": "40px"}),

        # -----------------------------
        # Control Bar (Region + Trend + Lookback)
        # -----------------------------
        dbc.Row(
            [
                # Region selector
                dbc.Col(
                    dcc.Dropdown(
                        id="region-select",
                        options=[
                            {"label": "UK Sectors", "value": "UK"},
                            {"label": "US Sectors", "value": "US"},
                            {"label": "Metals", "value": "METALS"},
                            {"label": "Crypto", "value": "CRYPTO"},
                        ],
                        value="UK",
                        clearable=False,
                        style={"fontSize": "14px"}
                    ),
                    width=2,
                    style={"paddingRight": "10px"}
                ),

                # Trend mode selector
                dbc.Col(
                    dcc.Dropdown(
                        id="trend-mode",
                        options=[
                            {"label": "Pulse Count", "value": "pulse"},
                            {"label": "Weighted Pulses", "value": "weighted"},
                            {"label": "RSI", "value": "rsi"},
                            {"label": "MACD", "value": "macd"},
                        ],
                        value="pulse",
                        clearable=False,
                        style={"fontSize": "14px"}
                    ),
                    width=3,
                    style={"paddingRight": "10px"}
                ),

                # Lookback slider
                dbc.Col(
                    html.Div(
                        dcc.Slider(
                            id="lookback-slider",
                            min=5,
                            max=365,
                            step=5,
                            value=30,
                            marks={i: str(i) for i in [5, 30, 90, 180, 365]},
                        ),
                        style={"paddingTop": "8px"}
                    ),
                    width=7
                ),
            ],
            align="center",
            style={"marginBottom": "25px"}
        ),

        # -----------------------------
        # Bootstrap Tabs (Charts / Heatmap / Quadrant)
        # -----------------------------
        dbc.Tabs(
            [
                # -----------------------------
                # Charts Tab
                # -----------------------------
                dbc.Tab(
                    label="Charts",
                    tab_id="charts",
                    children=[
                        html.Div(
                            id="charts-container",
                            style={
                                "border": "1px solid #D3D3D3",
                                "padding": "10px",
                                "marginTop": "-10px",
                                "borderRadius": "10px",
                                "backgroundColor": "white"
                            }
                        )
                    ],
                    style={
                        "border": "1px solid #D3D3D3",
                        "paddingTop": "5px",
                        "borderRadius": "10px"
                    }
                ),

                # -----------------------------
                # Heatmap Tab
                # -----------------------------
                dbc.Tab(
                    label="Heatmap",
                    tab_id="heatmap",
                    children=[
                        html.Div(
                            id="heatmap-container",
                            style={
                                "border": "1px solid #D3D3D3",
                                "padding": "10px",
                                "marginTop": "-10px",
                                "borderRadius": "10px",
                                "backgroundColor": "white"
                            }
                        )
                    ],
                    style={
                        "border": "1px solid #D3D3D3",
                        "paddingTop": "5px",
                        "borderRadius": "10px"
                    }
                ),

                # -----------------------------
                # Quadrant Tab
                # -----------------------------
                dbc.Tab(
                    label="Quadrant",
                    tab_id="quadrant",
                    children=[
                        html.Div(
                            id="quadrant-container",
                            style={
                                "border": "1px solid #D3D3D3",
                                "padding": "10px",
                                "marginTop": "-10px",
                                "borderRadius": "10px",
                                "backgroundColor": "white"
                            }
                        )
                    ],
                    style={
                        "border": "1px solid #D3D3D3",
                        "paddingTop": "5px",
                        "borderRadius": "10px"
                    }
                ),
            ],
            id="sector-subtabs",
            active_tab="charts",
            style={"marginBottom": "20px"}
        ),

    ]),
    style={"backgroundColor": "#f8f9fa", "marginTop": "20px", "padding": "20px"},
    className="mb-4 shadow-sm"
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
                dbc.Tab(homepage_content, label="Home"),   
                dbc.Tab(treemap_content, label="Tree Maps"),
                dbc.Tab(advanced_filter, label="Advanced Filter"),
                dbc.Tab(propage_content, label="Pro Analysis"),
                dbc.Tab(sector_indicies_content, label="Global Sector Analysis"),
                dbc.Tab(Calculator, label="Calculator"),
                
        ]),
   ]),

], fluid=True)


def get_gauge_values(ticker, country, df):

    df.columns = df.columns.str.strip()

    row = df[df["Ticker"] == ticker]

    if not row.empty:
        volume_raw_actual = row["Avg Volume"].values[0]
        volume_raw = row["Volume Indicator"].values[0]
        beta_raw = row["Beta Risk"].values[0]

        volume = 0 if str(volume_raw).strip().upper() == "UNKNOWN" else float(volume_raw)
        beta = -5 if str(beta_raw).strip().upper() == "UNKNOWN" else float(beta_raw)

        # Clamp values
        volume = max(0, min(volume, 10))
        beta = max(-5, min(beta, 5))

        return volume, beta, volume_raw_actual, beta_raw

    return 0, 5  # Fallback values
    
 
def get_buysell_signals(ticker, country, df_buysell):

    filtered = df_buysell[df_buysell["Ticker"] == ticker].copy()

    if not filtered.empty:
        total_profit = filtered["Profit"].sum()
        summary_row = {
            "Profit": round(total_profit, 2), "is_summary": True
        }
        filtered = pd.concat([filtered, pd.DataFrame([summary_row])], ignore_index=True)

    return filtered.to_dict("records")
    
@app.callback(
    Output("line-graph", "figure"),
    Output("macd-graph", "figure"),
    Output("rsi-graph", "figure"),
    Output("ema-graph", "figure"),
    Output("buy-sell-table", "rowData"),
    Output("volume-gauge", "value"),
    Output("beta-gauge", "value"),
    Output("dynamic-tab", "label"),
    Output("news_articles", "rowData"),
    Output("current-price", "children"),
    Output("52weeklow-price", "children"),
    Output("52weekhigh-price", "children"),
    Output("volume-raw", "children"),
    Output("beta-raw", "children"),
    Input("company_industry_list", "selectedRows"),
    State("country-store", "data"),
    State("store-df-batch", "data"),
    State("store-df-buysell", "data"),
    prevent_initial_call=True
)
def update_stock_chart(selected_rows, country, df_data, df_buysell_data):

    if selected_rows:
        ticker = selected_rows[0]['Ticker']
        selected_company = selected_rows[0]['Name']

        try:
            hist = yf.download(ticker, period="1y", interval="1d", auto_adjust=False, progress=False)
            hist.reset_index(inplace=True)
            hist.columns = [col if isinstance(col, str) else col[0] for col in hist.columns]
            hist.rename(columns={"Date": "Datetime"}, inplace=True)

            if hist.empty:
                empty_fig = px.line(title=f"No data available for {ticker}")
                return empty_fig, empty_fig, empty_fig, empty_fig, [], 0, 0, "No Selection", [], 0.00, 0.00, 0.00, 0.00, "UNKNOWN"

            # ── Line Chart
            high_52week = hist["High"].max()
            low_52week = hist["Low"].min()

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

            # ────────────────────────────────────────────────
            # NEW: Generate MACD, RSI, EMA using helper
            # ────────────────────────────────────────────────
            fig_macd, fig_rsi, fig_ema = generate_indicator_charts(
                hist, ticker, selected_company, graph_properties
            )

            # ── Load DataFrames
            df = pd.DataFrame(df_data)
            df_buysell = pd.DataFrame(df_buysell_data)

            # ── Buy/Sell Signals
            signal_data = get_buysell_signals(ticker, country, df_buysell)

            # ── Gauges
            volume_val, beta_val, volume_raw, beta_raw = get_gauge_values(ticker, country, df)

            # ── News
            news_data = get_news_data(ticker)

            # ── Last Close
            last_close = hist["Close"].iloc[-1]

            return (
                fig_line,
                fig_macd,
                fig_rsi,
                fig_ema,
                signal_data,
                volume_val,
                beta_val,
                selected_company,
                news_data,
                f"{last_close:.2f}",
                f"{low_52week:.2f}",
                f"{high_52week:.2f}",
                volume_raw,
                beta_raw
            )

        except Exception as e:
            error_fig = px.line(title=f"Error: {e}")
            return (
                error_fig, error_fig, error_fig, error_fig,
                [], 0, 0, "No Selection", [],
                0.00, 0.00, 0.00, 0.00, "UNKNOWN"
            )

    return (
        go.Figure(), go.Figure(), go.Figure(), go.Figure(),
        [], 0, 0, "No Selection", [],
        0.00, 0.00, 0.00, 0.00, "UNKNOWN"
    )



def generate_indicator_charts(hist, ticker, selected_company, graph_properties):
    """
    Returns: fig_macd, fig_rsi, fig_ema
    """

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
    fig_ema.update_layout(
        title=f"{ticker}: {selected_company}",
        plot_bgcolor='white',
        legend=dict(orientation="h", yanchor="top", y=1.2, xanchor="right", x=1)
    )
    fig_ema.update_xaxes(**graph_properties)
    fig_ema.update_yaxes(**graph_properties)

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
    fig_rsi.update_layout(
        title=f"{ticker}: {selected_company}",
        plot_bgcolor='white',
        legend=dict(orientation="h", yanchor="top", y=1.2, xanchor="right", x=1)
    )
    fig_rsi.update_xaxes(**graph_properties)
    fig_rsi.update_yaxes(**graph_properties)

    # ── MACD
    exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
    exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
    hist['MACD'] = exp1 - exp2
    hist['Signal Line'] = hist['MACD'].ewm(span=9, adjust=False).mean()
    hist['MACD Histogram'] = hist['MACD'] - hist['Signal Line']

    # Smooth histogram
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
        title=f"{ticker}: {selected_company}",
        plot_bgcolor='white',
        legend=dict(orientation="h", yanchor="top", y=1.2, xanchor="right", x=1)
    )
    fig_macd.update_xaxes(**graph_properties)
    fig_macd.update_yaxes(**graph_properties)

    return fig_macd, fig_rsi, fig_ema








# Function to retrieve data for multiple ticker symbols
def clean_keywords(raw_text):
    stopwords = {
        'plc', 'ord', 'gbp', 'limited', 'inc', 'group', 'corporation', 'company',
        'one', '&', 'co', 'llc', 'ltd', 'holdings', 'stock', 'share', 'unit', 'other'
    }

    cleaned_text = re.sub(r'[^\w\s]', ' ', raw_text.lower())  # Remove punctuation
    tokens = cleaned_text.split()

    filtered_tokens = []
    for t in tokens:
        if t in stopwords:
            continue
        if t.isnumeric():  # Remove pure digits
            continue
        if re.match(r'^[a-z]{3}\d*\.?\d*$', t):  # Remove currency codes like gbp0001
            continue
        if len(t) <= 2:
            continue
        filtered_tokens.append(t)

    return filtered_tokens


def get_news_data(ticker_symbol):
    search_url = "https://query2.finance.yahoo.com/v1/finance/search"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    news_data = []

    try:
        # Step 1: Initial metadata request
        response = requests.get(search_url, params={"q": ticker_symbol}, headers=headers)
        response.raise_for_status()
        data = response.json()
        #print(data)
        quote = data.get('quotes', [{}])[0]

        longname = quote.get('longname', "")
        shortname = quote.get('shortname', "")
        sector = quote.get('sector', "")
        industry = quote.get('industry', "")

        raw_text = f"{longname} {shortname} {sector} {industry}"
        sector_keywords = list(set(clean_keywords(raw_text)))

        #print(f"🔍 Using refined keywords for filtering → {sector_keywords}")
        
        news_response = requests.get(
            f"https://query2.finance.yahoo.com/v1/finance/search?q={longname}",
            headers=headers
        )
        
        news_response.raise_for_status()
        news_json = news_response.json()
        news_articles = news_json.get("news", [])

        local_timezone = tzlocal.get_localzone()

        def is_sector_relevant(article, keywords):
            text = (article.get("title", "") + article.get("summary", "")).lower()
            return any(kw in text for kw in keywords)

        for article in news_articles:
            if sector_keywords and not is_sector_relevant(article, sector_keywords):
                continue

            news_title = article.get("title", "")
            publisher = article.get("publisher", "")
            news_link = article.get("link", "")
            pub_date_unix = article.get("providerPublishTime", 0)
            related_tickers = article.get("relatedTickers", [])

            pub_date = datetime.fromtimestamp(pub_date_unix, local_timezone)
            formatted_link = f'<a href="{news_link}" target="_blank">{news_title}</a>'
            actual_ticker = related_tickers[0] if related_tickers else ticker_symbol

            news_data.append({
                "Date": pub_date,
                "Ticker": actual_ticker,
                "link": formatted_link,
                "publisher": publisher
            })

        if ticker_symbol.endswith(".L"):
            news_items = extract_rns_news(ticker_symbol)
            news_data.extend(news_items)
        else:
            news_items = extract_us_stock_news(ticker_symbol)
            news_data.extend(news_items)

        # Step 4: Sort all news by date (most recent first)
        news_data.sort(key=lambda x: x["Date"], reverse=True)
        
        return news_data

    except Exception as e:
        print(f"❌ Error fetching news for {ticker_symbol}: {e}")
        return []



def extract_rns_news(ticker: str, per_page: int = 300):
    # Remove '.L' suffix if present
    news_rns = []
    
    if ticker.endswith(".L"):
        actual_ticker = ticker.removesuffix(".L")

        url = f"https://www.investegate.co.uk/company/{actual_ticker}?perPage={per_page}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data for {ticker}. Status code: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="table-investegate")
        if not table:
            raise Exception("Could not find the expected table on the page.")

        
        rows = table.find("tbody").find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            # Extract and parse date and time
            date_str = cols[0].get_text(strip=True)
            time_str = cols[1].get_text(strip=True)

            try:
                dt = datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %I:%M %p")
                dt = dt.replace(tzinfo=ZoneInfo("Europe/London"))
            except Exception:
                continue  # Skip rows with invalid date/time

            # Extract publisher
            publisher_tag = cols[2].find("a", class_="source-RNS")
            publisher = publisher_tag.get_text(strip=True) if publisher_tag else "Unknown"

            # Extract announcement link and text
            announcement_tag = cols[3].find("a", class_="announcement-link")
            if not announcement_tag:
                continue

            href = announcement_tag["href"]
            text = announcement_tag.get_text(strip=True)
            formatted_link = f'<a href="{href}" target="_blank">{text}</a>'

            news_rns.append({
                "Date": dt,
                "Ticker": ticker,  # Keep original input with ".L"
                "link": formatted_link,
                "publisher": publisher
            })

        #return news_rns
    return news_rns


def extract_us_stock_news(ticker: str):
    news_items = []
    url = f"https://www.mql5.com/en/quotes/stocks/{ticker.upper()}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data for {ticker}. Status code: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    news_section = soup.find("div", class_="nav-symbol__section nav-symbol__news")
    if not news_section:
        return news_items

    for li in news_section.select("ul.nav-symbol__news-list li"):
        # Extract source
        source_tag = li.find("span", class_="news-source")
        publisher = source_tag.get("title") if source_tag else "Unknown"

        # Extract datetime
        time_tag = li.find("time")
        try:
            dt = datetime.strptime(time_tag["datetime"], "%Y-%m-%dT%H:%MZ")
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        except Exception:
            continue

        # Extract link and title
        title_tag = li.find("span", class_="news-title").find("a")
        if not title_tag:
            continue

        href = title_tag["href"]
        text = title_tag.get("title", title_tag.get_text(strip=True))
        formatted_link = f'<a href="{href}" target="_blank">{text}</a>'

        news_items.append({
            "Date": dt,
            "Ticker": ticker.upper(),
            "link": formatted_link,
            "publisher": publisher
        })

    return news_items




@app.callback(
    Output("advanced-filter-store", "data"),
    Input("apply-filters-btn", "n_clicks"),
    State("filter-sector", "value"),
    State("filter-industry", "value"),
    State("filter-hold-period", "value"),
    State("filter-transactions", "value"),
    State("filter-volume", "value"),
    State("filter-beta", "value"),
    State("filter-last-price", "value"),  # ← Add this
    State("filter-drop-samples", "value"),
    State("filter-ask-bid-spread", "value"),    
    prevent_initial_call=True
)
def store_advanced_filter(n, sector, industry, hold, transactions, volume, beta, last_price, dropped_samples, ask_bid):
    return {
        "sector": sector,
        "industry": industry,
        "hold_range": hold,
        "transactions_range": transactions,
        "volume_range": volume,
        "beta_range": beta,
        "last_price_range": last_price,
        "drop_samples_range": dropped_samples,
        "ask_bid_spread": ask_bid
    }
    
@app.callback(
    Output("advanced-filter-grid", "rowData"),
    Input("advanced-filter-store", "data"),
    #State("country-store", "data"),
    Input("country-store", "data"),  # ← make this an Input, not just State
    State("store-df-batch", "data")
)
def update_advanced_filtered_table(filter_data, country, df_data):
    #df, *_ = load_country_data(country)
    df = pd.DataFrame(df_data)
    df.columns = df.columns.str.strip()

    #filtered = df.copy()
    filtered = df
    
    # If no filter applied, return full data
    if not filter_data:
        return filtered.to_dict("records")



    if filter_data.get("sector"):
        filtered = filtered[filtered["Sector"].isin(filter_data["sector"])]

    if filter_data.get("industry"):
        filtered = filtered[filtered["Industry"].isin(filter_data["industry"])]

    hold_min, hold_max = filter_data["hold_range"]
    filtered = filtered[
        (filtered["Avg Hold Period(days)"] >= hold_min) &
        (filtered["Avg Hold Period(days)"] <= hold_max)
    ]
    
    trans_min, trans_max = filter_data["transactions_range"]
    filtered = filtered[
        (filtered["Num of Trades"] >= trans_min) &
        (filtered["Num of Trades"] <= trans_max)
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

    if "drop_samples_range" in filter_data:
        price_min, price_max = filter_data["drop_samples_range"]
        filtered["Dropped Samples %"] = pd.to_numeric(filtered["Dropped Samples %"], errors="coerce")
        filtered = filtered[
            (filtered["Dropped Samples %"] >= price_min) &
            (filtered["Dropped Samples %"] <= price_max)
        ]
        
    if "ask_bid_spread" in filter_data:
        price_min, price_max = filter_data["ask_bid_spread"]
        filtered["Ask-Bid Spread"] = pd.to_numeric(filtered["Ask-Bid Spread"], errors="coerce")
        filtered = filtered[
            (filtered["Ask-Bid Spread"] >= price_min) &
            (filtered["Ask-Bid Spread"] <= price_max)
        ]    

    return filtered.to_dict("records")
    

@app.callback(
    Output("last-price-label", "children"),
    Output("Beta-Risk-label", "children"),
    Input("filter-last-price", "value"),
    Input("filter-beta", "value")
)
def update_labels(price_range, beta_range):
    low_p, high_p = price_range
    low_b, high_b = beta_range
    return (
        f"Share Price Range: {low_p:,.2f} – {high_p:,.2f}",
        f"Beta Range: {low_b:,.2f} – {high_b:,.2f}"
    )

    

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
    return "", 1000, 0, 0, None, None, 11.99, 3.99, 0.005


@app.callback(
    Output("net-gain", "children"),
    Output("gain-value", "children"),
    Output("platform-fees", "children"),
    Output("trading-fees", "children"),
    Output("taxes", "children"),
    Output("net-gain-value", "children"),
    Output("company-name", "children"),
    Output("calculator-macd-performance-graph", "figure"),
    Output("calculator-rsi-performance-graph", "figure"),
    Output("calculator-ema-performance-graph", "figure"),
    Output("cal-buy-price", "children"),
    Output("cal-sell-price", "children"),
    Output("cal-num-shares", "children"),
    Output("cal-investment", "children"),
    Output("graphical-calculator-graph", "figure"),
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
    State("calc-taxes", "value"),
    State("desired-profit", "value")
)
def calculate_metrics(n_clicks, ticker, investment, mode, buy, sell, start_date, end_date, platform_fees, trading_fees, taxes, target_profit):
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
        return "0%", "0", "0", "0", "0", "0", "No Selection", go.Figure(), go.Figure(), go.Figure(), "0", "0", "0", "0", go.Figure()

    if not ticker or not isinstance(ticker, str) or not ticker.strip():
         return "0%", "0", "0", "0", "0", "0", "No Selection", go.Figure(), go.Figure(), go.Figure(), "0", "0", "0", "0", go.Figure()

    roi_percent, gain, net_gain_value, tax_amount = 0, 0, 0, 0
    
    if mode == "manual":
        if buy == 0 or sell == 0:
            return "0%", "0", "0", "0", "0", "0", "No Selection", go.Figure(), go.Figure(), go.Figure(), "0", "0", "0", "0", go.Figure()
            
            
    # ------------------------- # MANUAL MODE # ------------------------- 
    if mode == "manual": 
        if buy == 0 or sell == 0: 
            return "0%", "0", "0", "0", "0", "0", "No Selection", go.Figure(), go.Figure(), go.Figure(), "0", "0", "0", "0", go.Figure() 
            
        # Remove buy-side trading fee 
        available_after_fee = investment - trading_fees 
        
        # Share cost before stamp duty 
        share_cost_before_tax = available_after_fee / (1 + taxes) 
        
        # Whole shares only 
        shares = int(share_cost_before_tax / buy) 
        
        # Actual share cost 
        actual_share_cost = shares * buy 
        
        # Stamp duty 
        stamp_duty = actual_share_cost * taxes 
        
        # Total cost of buying 
        total_buy_cost = actual_share_cost + stamp_duty + trading_fees 
        
        # Selling proceeds 
        sell_value = shares * sell
        
        # Net gain (subtract sell fee) 
        net_gain_value = sell_value - total_buy_cost - trading_fees 
        
        # Gross gain (before fees & taxes) 
        gain = sell_value - actual_share_cost 
        
        # ROI 
        roi_percent = round((net_gain_value / investment) * 100, 2) if investment else 0 
            
        # Stamp duty for display 
        tax_amount = stamp_duty 
            
        # Manual mode has no platform fees 
        total_platform_fees = 0 
        data = yf.download(ticker, period="1y", auto_adjust=True) 
        calculated_buy_price = buy 
        calculated_sell_price = sell 
        calculated_num_shares = shares
        

    elif mode == "date":
        if not all([ticker, start_date, end_date]):
            print(F"MODE ERROR: ticker:{ticker}, start_date{start_date}, end_date{end_date}")
            return "0%", "0", f"{platform_fees}", f"{trading_fees * 2}", "0", "0", "No Selection", go.Figure(), go.Figure(), go.Figure(), "0", "0", "0", "0", go.Figure()
            
        #check the dates are valid
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        
        if end_date_obj < start_date_obj:
            print("Date error:")
            return "0%", "0", f"{platform_fees}", f"{trading_fees * 2}", "0", "0", "No Selection", go.Figure(), go.Figure(), go.Figure(), "0", "0", "0", "0", go.Figure()

        try:
            # 🔍 Get historical data
            data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)

            if data.empty or "Close" not in data.columns:
                print(f"{data}")
                return "0%", "0", f"{platform_fees}", f"{trading_fees * 2}", "0", "0", "No Selection", go.Figure(), go.Figure(), go.Figure(), "0", "0", "0", "0", go.Figure()

            buy = float(data['Close'].iloc[0].item())     # ✅ Preferred
            sell = float(data['Close'].iloc[-1].item())   # ✅ Last row safely too

            # calculate number of monhs elasped
            num_months = int((end_date_obj.year - start_date_obj.year) * 12 + end_date_obj.month - start_date_obj.month)
            if num_months > 1:
                total_platform_fees = float(platform_fees * num_months)
            
            #print (F"num_months:{num_months}, platform_fees{platform_fees}, total_platform_fees{total_platform_fees}")
            
            # Remove buy fee 
            available_after_fee = investment - trading_fees 
            # Share cost before stamp duty 
            share_cost_before_tax = available_after_fee / (1 + taxes) 
            # Whole shares 
            shares = int(share_cost_before_tax / buy) 
            # Actual share cost 
            actual_share_cost = shares * buy 
            # Stamp duty 
            stamp_duty = actual_share_cost * taxes 
            # Total buy cost 
            total_buy_cost = actual_share_cost + stamp_duty + trading_fees 
            # Selling proceeds 
            sell_value = shares * sell 
            # Net gain 
            net_gain_value = sell_value - total_buy_cost - trading_fees - total_platform_fees 
            # Gross gain 
            gain = sell_value - actual_share_cost 
            # ROI 
            roi_percent = round((net_gain_value / investment) * 100, 2) if investment else 0 
            tax_amount = stamp_duty 
            calculated_buy_price = buy 
            calculated_sell_price = sell 
            calculated_num_shares = shares

        except Exception:
            return "0%", "0", f"{total_platform_fees}", f"{trading_fees * 2}", "0", "0", "No Selection", go.Figure(), go.Figure(), go.Figure(), "0", "0", "0", "0", go.Figure()
        
        
    company_long_name = get_company_info(ticker)
    
    if not data.empty:
        
        # Convert to a uniform structure like your other callback 
        #hist = data.reset_index() 
        #hist.rename(columns={"Date": "Datetime"}, inplace=True)
        hist = yf.download(ticker, period="1y", interval="1d", auto_adjust=False, progress=False)
        hist.reset_index(inplace=True)
        hist.columns = [col if isinstance(col, str) else col[0] for col in hist.columns]
        hist.rename(columns={"Date": "Datetime"}, inplace=True)    
        
        # Generate MACD, RSI, EMA charts 
        fig_macd, fig_rsi, fig_ema = generate_indicator_charts( hist, ticker, company_long_name, graph_properties ) 
        
        fig_graphical_calculator = update_graphical_calculator(ticker, buy, target_profit, investment, taxes, trading_fees)

    return (
        f"{roi_percent}%",
        f"{round(gain, 2)}",
        f"{round(total_platform_fees, 2)}",
        f"{round(trading_fees * 2, 2)}",
        f"{round(tax_amount, 2)}",
        f"{round(net_gain_value, 2)}",
        f"{company_long_name}",
        fig_macd,
        fig_rsi,
        fig_ema,
        f"{round(calculated_buy_price,6)}",
        f"{round(calculated_sell_price,6)}",
        f"{int(calculated_num_shares)}",
        f"{round(total_buy_cost, 2)}",
        fig_graphical_calculator
    )



# --- Callback: Click to reveal filename ---
@app.callback(
    Output("filename-box", "value"),
    Input("exchange-chart", "clickData"),
    State("country-store", "data"),
    State("store-padded-filenames", "data"),
    prevent_initial_call=True
)
def populate_filename(click_data, country, filenames):
    if not click_data:
        return ""

    # Unpack everything needed, especially padded_filenames
    #_, _, padded_filenames, _, _ = load_country_data(country)
    padded_filenames = filenames

    point_index = click_data["points"][0]["pointIndex"]
    
    if 0 <= point_index < len(padded_filenames):
        filename = padded_filenames[point_index]
        
        #print(f"Selected filename: {filename}")
        #print(f"Full path: {os.path.join(DATA_ROOT, country, filename)}")
        
        return filename if filename else ""
    
    return ""

# --- Callback: Download file from assets ---
@app.callback(
    Output('download', 'data'),
    Input('download-btn', 'n_clicks'),
    State('filename-box', 'value'),
    State('country-store', 'data'),  # ← Add this
    #prevent_initial_call=True
)
def serve_file(n_clicks, filename, country):
    
    if filename:
        file_path_raw_data = os.path.join(DATA_ROOT, country, filename)
        #print(f"[Download Triggered] Country: {country}, Filename: {filename}")
        #print(f"[Full Path] {file_path_raw_data}")
        
        if os.path.exists(file_path_raw_data):
            return send_file(file_path_raw_data)
    return None
    
    
    
@app.callback(
    Output("store-df-batch", "data"),
    Output("store-df-buysell", "data"),
    Output("store-padded-filenames", "data"),
    Output("store-padded-values", "data"),
    Output("store-sector-options", "data"),
    Output("country-store", "data"),
    Input("country-selector", "value")
)
def save_country_selection(selected_country):

    df, df_buysell, padded_filenames, padded_values, sector_options = load_country_data(selected_country)
    
    # Convert DataFrames to JSON-serializable format
    df_json = df.to_dict("records")
    df_buysell_json = df_buysell.to_dict("records")
    
    #return selected_country
    return df_json, df_buysell_json, padded_filenames, padded_values, sector_options, selected_country


@app.callback(
    Output("exchange-chart", "figure"),
    Output("bar-graph", "figure"),
    Output("company_industry_list", "rowData"),
    Output("selected-sector-store", "data"),
    Output("sector-button-container", "children"),
    Output("sector-summary-container", "children"),
    Output("filename-box", "value", allow_duplicate=True),
    Input("country-store", "data"),
    Input({'type': 'sector-btn', 'index': dash.ALL}, "n_clicks"),
    Input("bar-graph", "clickData"),
    State("selected-sector-store", "data"),
    State("store-df-batch", "data"),
    State("store-padded-values", "data"),
    prevent_initial_call=True
)
def update_homepage(country, n_clicks_list, click_data, stored_sector, df_data, stored_padded_values):

    #df, _, _, padded_values, _ = load_country_data(country)
    df = pd.DataFrame(df_data)
    padded_values = stored_padded_values
    main_figure = create_figure(padded_values, country)


    # Sector totals
    sector_profits = df.groupby("Sector")["Total Profit"].sum()
    total_profit = sector_profits.sum()

    sector_cards = [
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5(sector, className="card-title"),
                    html.H6(f"{profit:,.2f}", className="card-subtitle text-success mb-0")
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

    sector_summary = dbc.Card(
        dbc.CardBody([
            html.H4(f"Total Profit: {total_profit:,.2f}", className="text-primary mb-4"),
            html.H5("Sector Overview", className="mb-3"),
            dbc.Row(sector_cards, className="gx-3", align="stretch")
        ]),
        className="mb-4",
        style={"backgroundColor": "#f8f9fa"}
    )


    triggered = ctx.triggered_id
    all_sectors = df["Sector"].dropna().unique()
    selected_sector = stored_sector  # ← default from store
    
    # Set the default selected sector on first load
    if not stored_sector and len(all_sectors) > 0:
        selected_sector = all_sectors[0]
    else:
        selected_sector = stored_sector

    # Override if a sector button is clicked

   
    if isinstance(triggered, dict) and triggered.get("type") == "sector-btn":
        selected_sector = triggered["index"]  # ← override if button clicked


    buttons = html.Div(
        dbc.ButtonGroup([
            dbc.Button(
                sector,
                id={"type": "sector-btn", "index": sector},
                color="primary" if sector == selected_sector else "secondary",
                outline=sector != selected_sector,
                active=sector == selected_sector
            )
            for sector in all_sectors
        ]),
        style={"display": "flex", "justifyContent": "center"}
    )

    filtered_df = df[df["Sector"] == selected_sector]

    if click_data and click_data.get("points"):
        clicked_industry = click_data["points"][0]["x"]
        filtered_df = filtered_df[filtered_df["Industry"] == clicked_industry]

    industry_totals = df[df["Sector"] == selected_sector].groupby("Industry")["Total Profit"].sum().reset_index()

    bar_figure = px.bar(
        industry_totals,
        x="Industry",
        y="Total Profit",
        title=f"Total Profit by Industry in {selected_sector}",
        labels={"Total Profit": "Total Profit", "Industry": "Industry"},
        text_auto=".2s"
    )
    bar_figure.update_traces(marker_color="#ebf5ff", marker_line=dict(width=1.2, color="#78afd9"))
    bar_figure.update_layout(
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        font=dict(family="Segoe UI", size=14),
        margin=dict(t=60, l=40, r=20, b=40),
        title_font=dict(size=20, family="Segoe UI", color="#333"),
        xaxis=dict(mirror=True, ticks='outside', showline=True, linecolor='lightgrey'),
        yaxis=dict(mirror=True, ticks='outside', showline=True, linecolor='lightgrey')
    )

    return main_figure, bar_figure, filtered_df.to_dict("records"), selected_sector, buttons, sector_summary, ""


def treemap_get_company_info_batched(ticker_list, batch_size=50):
    DEFAULT_UNKNOWN = "UNKNOWN"
    results = []

    def format_float(val, default=DEFAULT_UNKNOWN):
        return f"{val:.2f}" if isinstance(val, (int, float)) else default

    def treemap_process_batch(batch):
        try:
            tickers_data = yf.Tickers(" ".join(batch))
            tickers = tickers_data.tickers
        except Exception as e:
            print(f"⚠️ Error fetching batch: {e}")
            return

        for symbol in batch:
            try:
                info = tickers[symbol].info
                market_cap = info.get("marketCap")
                if not isinstance(market_cap, (int, float)):
                    continue

                price = format_float(info.get("regularMarketPrice"))
                price_change = format_float(info.get("regularMarketChange"))
                percent_change = info.get("regularMarketChangePercent", 0.0)
                percent_change = float(percent_change) if isinstance(percent_change, (int, float)) else 0.0
                #long_name = info.get("longName", DEFAULT_UNKNOWN)

                # Common metadata fields
                common_fields = {
                    "Market Cap": market_cap,
                    "Symbol": symbol,
                    #"Short Name": info.get("shortName", DEFAULT_UNKNOWN),
                    "Long Name": info.get("longName", DEFAULT_UNKNOWN),
                    #"Exchange": info.get("exchange", DEFAULT_UNKNOWN),
                    #"Quote Type": info.get("quoteType", DEFAULT_UNKNOWN),
                    #"Currency": info.get("currency", DEFAULT_UNKNOWN),
                    #"Financial Currency": info.get("financialCurrency", DEFAULT_UNKNOWN),
                    #"Region": info.get("region", DEFAULT_UNKNOWN),
                    #"Language": info.get("language", DEFAULT_UNKNOWN),
                    #"Quote Source": info.get("quoteSourceName", DEFAULT_UNKNOWN),
                    #"Market State": info.get("marketState", DEFAULT_UNKNOWN),
                    #"Full Exchange Name": info.get("fullExchangeName", DEFAULT_UNKNOWN),
                    #"Exchange Timezone": info.get("exchangeTimezoneName", DEFAULT_UNKNOWN),
                    #"Exchange TZ Short": info.get("exchangeTimezoneShortName", DEFAULT_UNKNOWN),
                    #"GMT Offset (ms)": info.get("gmtOffSetMilliseconds", DEFAULT_UNKNOWN),
                    #"Market": info.get("market", DEFAULT_UNKNOWN),
                    "Price": price,
                    "Price Change": price_change,
                    "Percent Change": percent_change,
                    #"Previous Close": info.get("previousClose", DEFAULT_UNKNOWN),
                    #"Open": info.get("open", DEFAULT_UNKNOWN),
                    "Day Low": info.get("dayLow", DEFAULT_UNKNOWN),
                    "Day High": info.get("dayHigh", DEFAULT_UNKNOWN),
                    #"Regular Market Previous Close": info.get("regularMarketPreviousClose", DEFAULT_UNKNOWN),
                    #"Regular Market Open": info.get("regularMarketOpen", DEFAULT_UNKNOWN),
                    #"Regular Market Day Low": info.get("regularMarketDayLow", DEFAULT_UNKNOWN),
                    #"Regular Market Day High": info.get("regularMarketDayHigh", DEFAULT_UNKNOWN),
                    #"Regular Market Day Range": info.get("regularMarketDayRange", DEFAULT_UNKNOWN),
                    #"Volume": info.get("volume", DEFAULT_UNKNOWN),
                    #"Regular Market Volume": info.get("regularMarketVolume", DEFAULT_UNKNOWN),
                    "Average Volume": info.get("averageVolume", DEFAULT_UNKNOWN),
                    #"Average Volume 10D": info.get("averageVolume10days", DEFAULT_UNKNOWN),
                    #"Average Daily Volume 10D": info.get("averageDailyVolume10Day", DEFAULT_UNKNOWN),
                    #"Average Daily Volume 3M": info.get("averageDailyVolume3Month", DEFAULT_UNKNOWN),
                    #"Trailing PE": info.get("trailingPE", DEFAULT_UNKNOWN),
                    #"EPS (TTM)": info.get("epsTrailingTwelveMonths", DEFAULT_UNKNOWN),
                    #"Price to Book": info.get("priceToBook", DEFAULT_UNKNOWN),
                    #"Book Value": info.get("bookValue", DEFAULT_UNKNOWN),
                    "52W Low": info.get("fiftyTwoWeekLow", DEFAULT_UNKNOWN),
                    "52W High": info.get("fiftyTwoWeekHigh", DEFAULT_UNKNOWN),
                    #"52W Range": info.get("fiftyTwoWeekRange", DEFAULT_UNKNOWN),
                    #"52W Low Change": info.get("fiftyTwoWeekLowChange", DEFAULT_UNKNOWN),
                    #"52W Low Change %": info.get("fiftyTwoWeekLowChangePercent", DEFAULT_UNKNOWN),
                    #"52W High Change": info.get("fiftyTwoWeekHighChange", DEFAULT_UNKNOWN),
                    #"52W High Change %": info.get("fiftyTwoWeekHighChangePercent", DEFAULT_UNKNOWN),
                    #"52W Change %": info.get("fiftyTwoWeekChangePercent", DEFAULT_UNKNOWN),
                    #"50D Avg": info.get("fiftyDayAverage", DEFAULT_UNKNOWN),
                    #"200D Avg": info.get("twoHundredDayAverage", DEFAULT_UNKNOWN),
                    #"50D Avg Change": info.get("fiftyDayAverageChange", DEFAULT_UNKNOWN),
                    #"50D Avg Change %": info.get("fiftyDayAverageChangePercent", DEFAULT_UNKNOWN),
                    #"200D Avg Change": info.get("twoHundredDayAverageChange", DEFAULT_UNKNOWN),
                    #"200D Avg Change %": info.get("twoHundredDayAverageChangePercent", DEFAULT_UNKNOWN),
                    "Bid": info.get("bid", DEFAULT_UNKNOWN),
                    "Ask": info.get("ask", DEFAULT_UNKNOWN),
                    #"Bid Size": info.get("bidSize", DEFAULT_UNKNOWN),
                    #"Ask Size": info.get("askSize", DEFAULT_UNKNOWN),
                    #"Tradeable": info.get("tradeable", DEFAULT_UNKNOWN),
                    #"Crypto Tradeable": info.get("cryptoTradeable", DEFAULT_UNKNOWN),
                    #"Custom Alert Confidence": info.get("customPriceAlertConfidence", DEFAULT_UNKNOWN),
                    #"Triggerable": info.get("triggerable", DEFAULT_UNKNOWN),
                    #"Earnings Start": info.get("earningsTimestampStart", DEFAULT_UNKNOWN),
                    #"Earnings End": info.get("earningsTimestampEnd", DEFAULT_UNKNOWN),
                    #"Is Earnings Estimate": info.get("isEarningsDateEstimate", DEFAULT_UNKNOWN),
                    #"Max Age": info.get("maxAge", DEFAULT_UNKNOWN),
                    #"Price Hint": info.get("priceHint", DEFAULT_UNKNOWN),
                    #"Source Interval": info.get("sourceInterval", DEFAULT_UNKNOWN),
                    #"Exchange Data Delay": info.get("exchangeDataDelayedBy", DEFAULT_UNKNOWN),
                    #"Corporate Actions": info.get("corporateActions", DEFAULT_UNKNOWN)
                }
                
                # Final label for treemap
                label = f"""
                            <span style='font-family:monospace;'>
                            
                            <br>Name:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>[{common_fields.get('Symbol')}] {common_fields.get('Long Name')}</b>
                            <br>Price:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{price}
                            <br>Price Change:&nbsp;&nbsp;{price_change} ({percent_change:.2f}%)
                            <br>Ask (Buy):&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{common_fields.get('Ask')}
                            <br>Bid (Sell):&nbsp;&nbsp;&nbsp;&nbsp;{common_fields.get('Bid')}
                            <br>
                            <br>Day Low:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{common_fields.get('Day Low')}
                            <br>Day High:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{common_fields.get('Day High')}
                            <br>52W Low:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{common_fields.get('52W Low')}
                            <br>52W High:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{common_fields.get('52W High')}
                            <br>
                            <br>Average<br>Volume:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{common_fields.get('Average Volume')}
                            <br>
                            </span>
                        """
                common_fields["Label"] = label
                
                common_fields["Tile Text"] = f"{symbol}<br>{percent_change:.2f}%"
                results.append(common_fields)
               

            except Exception as e:
                print(f"⚠️ Error extracting metrics for {symbol}: {e}")

    for i in range(0, len(ticker_list), batch_size):
        treemap_process_batch(ticker_list[i:i + batch_size])

    return pd.DataFrame(results)

# 🎨 Treemap builder
def create_treemap(df, sector, industry, selected_country):
    fig = px.treemap(
        df,
        path=["Label"],
        values="Market Cap",
        color="Percent Change",
        color_continuous_scale=[
            [0.0, "rgb(200, 0, 0)"],
            [0.4998, "rgb(255, 255, 255)"],
            [0.5002, "rgb(255, 255, 255)"],
            [1.0, "rgb(0, 200, 0)"]
        ],
        color_continuous_midpoint=0,
        
        range_color=[-5, 5] 
    )

    fig.update_traces(
        customdata=df[["Label"]],
        text=df["Tile Text"],
        textinfo="text",
        hovertemplate="%{customdata[0]}<extra></extra>",
    )

    fig.update_layout(
        title_text=f"Treemap of {selected_country}: {sector} / {industry}",
        title_font_size=22,
        height=800,
        #coloraxis_showscale=False
    )

    return fig


@app.callback(
    Output("stored-data", "data"),
    Output("treemap_sector-dropdown", "options"),
    Output("treemap_sector-dropdown", "value"),  # 👈 Clear selection
    Output("treemap_industry-dropdown", "value"),  # 👈 Clear selection
    Output("treemap-output", "figure", allow_duplicate=True),
    Input("country-store", "data"),
    State("store-df-batch", "data"),
    #State("store-df-buysell", "data"),
    State("store-sector-options", "data"),
    prevent_initial_call=True
)
def update_all_on_country_change(selected_country, df_data, df_sector_options):
    if not selected_country:
        return no_update, no_update, no_update, no_update, no_update

    # Load full country data
    #df_batch, df_buysell, _, _, sector_options = load_country_data(selected_country)
    
    # Reconstruct DataFrames from stored data
    df_batch = pd.DataFrame(df_data)
    ### Vip removed df_buysell
    #df_buysell = pd.DataFrame(df_buysell_data)
    sector_options = df_sector_options  # Already a list
    # Format sector dropdown
    #sector_dropdown_options = [{"label": s, "value": s} for s in sector_options]

    # Format sector dropdown
    if df_sector_options is None or not isinstance(df_sector_options, list):
        sector_dropdown_options = []
    else:
        sector_dropdown_options = [{"label": s, "value": s} for s in df_sector_options]


    # Clear both dropdowns and treemap
    return (
        df_batch.to_dict("records"),
        sector_dropdown_options,
        None,  # Clear sector selection
        None,  # Clear industry selection
        go.Figure()  # Reset treemap
    )




# 🔁 Update industry dropdown

@app.callback(
    Output("treemap_industry-dropdown", "options"),
    Input("treemap_sector-dropdown", "value"),
    State("stored-data", "data")
)
def update_industry_options(selected_sector, stored_df):
    if not selected_sector or not stored_df:
        return []
    df = pd.DataFrame(stored_df)
    industries = sorted(df[df["Sector"] == selected_sector]["Industry"].dropna().unique())
    return [{"label": i, "value": i} for i in industries]

# 🔁 Generate treemap
@app.callback(
    Output("treemap-output", "figure"),
    Output("treemap_submit-button", "disabled"),
    Input("treemap_submit-button", "n_clicks"),
    State("treemap_sector-dropdown", "value"),
    State("treemap_industry-dropdown", "value"),
    State("stored-data", "data"),
    State("country-store", "data")
)
def update_treemap(n_clicks, selected_sector, selected_industry, stored_df, selected_country):
    if not selected_sector or not selected_industry or not stored_df:
        return px.scatter(title="Please select both Sector and Industry"), False

    df = pd.DataFrame(stored_df)
    filtered_df = df[
        (df["Sector"] == selected_sector) &
        (df["Industry"] == selected_industry)
    ]

    tickers = filtered_df["Ticker"].dropna().unique().tolist()
    if not tickers:
        return px.scatter(title="No tickers found for selection"), False

    df_info = treemap_get_company_info_batched(tickers)
    if df_info.empty:
        return px.scatter(title="No valid market cap data found"), False

    df_info["Market Cap"] = df_info["Market Cap"].apply(lambda x: x ** 0.5)
    return create_treemap(df_info, selected_sector, selected_industry, selected_country), False


#@app.callback(
#    Output("treemap_submit-button", "disabled", allow_duplicate=True),
#    Input("treemap_submit-button", "n_clicks"),
#    State("treemap_sector-dropdown", "value"),
#    State("treemap_industry-dropdown", "value"),
#    State("stored-data", "data"),
#    prevent_initial_call=True
#)
#def disbale_treemap_button(n_clicks, selected_sector, selected_industry, stored_df):
#    if not selected_sector or not selected_industry or not stored_df:
#        return False
#    else:
#        return True

# -----------------------------
# sector_indices_page
# -----------------------------
@app.callback(
    [
        Output("ranking-panel", "children"),
        Output("charts-container", "children"),
        Output("heatmap-container", "children"),
        Output("quadrant-container", "children"),
    ],
    [
        Input("lookback-slider", "value"),
        Input("trend-mode", "value"),
        Input("region-select", "value"),
        Input("sector-subtabs", "active_tab"),   # IMPORTANT
    ]
)
def update_sector_indices_page(lookback, mode, region, active_tab):

    # -----------------------------
    # Select dataset
    # -----------------------------
    if region == "UK":
        active_data = uk_sector_indices_data
    elif region == "US":
        active_data = us_sector_indices_data
    elif region == "METALS":
        active_data = metals_indices_data
    else:
        active_data = crypto_indices_data

    # ============================================================
    # 1. RANKING PANEL (always visible)
    # ============================================================
    ranking = []

    for name, df in active_data.items():
        df_slice = df.tail(lookback)

        if mode == "pulse":
            score = df_slice["DPCM_q"].sum()

        elif mode == "weighted":
            score = df_slice["DPCM_raw"].sum()

        elif mode == "rsi":
            delta = df_slice["Close"].diff()
            up = delta.clip(lower=0)
            down = -delta.clip(upper=0)
            roll_up = up.ewm(span=14, adjust=False).mean()
            roll_down = down.ewm(span=14, adjust=False).mean()
            rs = roll_up / roll_down
            rsi = 100 - (100 / (1 + rs))
            score = rsi.iloc[-1]

        elif mode == "macd":
            ema12 = df_slice["Close"].ewm(span=12, adjust=False).mean()
            ema26 = df_slice["Close"].ewm(span=26, adjust=False).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            score = (macd_line - signal_line).iloc[-1]

        ranking.append((name, score))

    ranking_sorted = sorted(ranking, key=lambda x: x[1], reverse=True)

    ranking_items = [
        html.Div(
            name,
            style={
                "padding": "8px 14px",
                "borderRadius": "12px",
                "backgroundColor": "rgb(200,255,200)" if score > 0 else "rgb(220,220,220)",
                "fontSize": "12px",
                "textAlign": "center",
                "marginRight": "6px",
                "marginBottom": "6px",
                "display": "inline-block",
            },
        )
        for name, score in ranking_sorted
    ]

    ranking_panel = html.Div(ranking_items)

    # ============================================================
    # 2. CHARTS TAB
    # ============================================================
    charts_output = ""
    if active_tab == "charts":

        graphs = []

        for name, df in active_data.items():

            df_slice = df.tail(lookback).copy()

            # -----------------------------
            # Ensure Close column exists
            # -----------------------------
            if "Close" not in df_slice or df_slice["Close"].isna().all():
                for alt in ["close", "Close Price", "Adj Close", "adj_close", "Price", "price"]:
                    if alt in df_slice and not df_slice[alt].isna().all():
                        df_slice["Close"] = df_slice[alt]
                        break
                if "Close" not in df_slice or df_slice["Close"].isna().all():
                    df_slice["Close"] = df_slice["DPCM_q"].cumsum()

            # -----------------------------
            # Weighted Pulses
            # -----------------------------
            if mode == "weighted":
                score = df_slice["DPCM_raw"].sum()
                direction = "UP" if score > 0 else "DOWN" if score < 0 else "NEUTRAL"

                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # ---------------------------------------
                # 1. Baseline trace (invisible)
                # ---------------------------------------
                fig.add_trace(go.Scatter(
                    x=df_slice.index,
                    y=[df_slice["Close"].min()] * len(df_slice),
                    mode="lines",
                    line=dict(color="rgba(0,0,0,0)"),
                    showlegend=False
                ), secondary_y=False)

                # ---------------------------------------
                # 2. Filled price line
                # ---------------------------------------
                fig.add_trace(go.Scatter(
                    x=df_slice.index,
                    y=df_slice["Close"],
                    mode="lines",
                    name="Sector Index",
                    fill='tonexty',   # <-- fills to the baseline, NOT to zero
                    fillcolor='rgba(214,235,255,0.5)',
                    line=dict(color='#78afd9', width=2)
                ), secondary_y=False)

                # ---------------------------------------
                # 3. Weighted pulses
                # ---------------------------------------
                fig.add_trace(go.Bar(
                    x=df_slice.index,
                    y=df_slice["DPCM_raw"],
                    name="Weighted Pulses",
                    marker_color="#78afd9",
                    opacity=0.6
                ), secondary_y=True)


            # -----------------------------
            # RSI
            # -----------------------------
            elif mode == "rsi":
                delta = df_slice["Close"].diff()
                up = delta.clip(lower=0)
                down = -delta.clip(upper=0)
                roll_up = up.ewm(span=14, adjust=False).mean()
                roll_down = down.ewm(span=14, adjust=False).mean()
                rs = roll_up / roll_down
                rsi = 100 - (100 / (1 + rs))
                rsi_last = rsi.iloc[-1]
                direction = "UP" if rsi_last > 55 else "DOWN" if rsi_last < 45 else "NEUTRAL"

                fig = make_subplots(specs=[[{"secondary_y": True}]])

                #fig.add_trace(go.Scatter(
                #    x=df_slice.index, y=df_slice["Close"],
                #    mode="lines", name="Sector Index",
                #    line=dict(color="black")
                #), secondary_y=False)

                fig.add_trace(go.Scatter(
                    x=df_slice.index, y=rsi,
                    mode="lines", name="RSI",
                    line=dict(color="#78afd9"),
                    fill='tozeroy',
                    fillcolor='rgba(214,235,255,0.5)'
                ), secondary_y=True)

                fig.add_trace(go.Scatter(
                    x=df_slice.index, y=[70]*len(df_slice),
                    mode="lines", name="Overbought (70)",
                    line=dict(color="grey", dash="dot")
                ), secondary_y=True)

                fig.add_trace(go.Scatter(
                    x=df_slice.index, y=[30]*len(df_slice),
                    mode="lines", name="Oversold (30)",
                    line=dict(color="green", dash="dot")
                ), secondary_y=True)

            # -----------------------------
            # MACD
            # -----------------------------
            elif mode == "macd":
                ema12 = df_slice["Close"].ewm(span=12, adjust=False).mean()
                ema26 = df_slice["Close"].ewm(span=26, adjust=False).mean()
                macd_line = ema12 - ema26
                signal_line = macd_line.ewm(span=9, adjust=False).mean()
                momentum = macd_line - signal_line

                direction = "UP" if macd_line.iloc[-1] > signal_line.iloc[-1] else \
                            "DOWN" if macd_line.iloc[-1] < signal_line.iloc[-1] else "NEUTRAL"

                fig = make_subplots(specs=[[{"secondary_y": True}]])

                #fig.add_trace(go.Scatter(
                #    x=df_slice.index, y=df_slice["Close"],
                #    mode="lines", name="Sector Index",
                #    line=dict(color="black")
                #), secondary_y=False)

                fig.add_trace(go.Scatter(
                    x=df_slice.index, y=macd_line,
                    mode="lines", name="MACD",
                    line=dict(color="green")
                ), secondary_y=True)

                fig.add_trace(go.Scatter(
                    x=df_slice.index, y=signal_line,
                    mode="lines", name="Signal Line",
                    line=dict(color="grey", dash="dot")
                ), secondary_y=True)

                fig.add_trace(go.Scatter(
                    x=df_slice.index, y=momentum,
                    mode="lines", name="Momentum",
                    fill='tozeroy',
                    fillcolor='rgba(214,235,255,0.5)',
                    line=dict(color="#78afd9")
                ), secondary_y=True)

            # -----------------------------
            # Pulse (DPCM_q)
            # -----------------------------
            else:
                score = df_slice["DPCM_q"].sum()
                direction = "UP" if score > 0 else "DOWN" if score < 0 else "NEUTRAL"

                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # ---------------------------------------
                # 1. Baseline trace (invisible)
                # ---------------------------------------
                fig.add_trace(go.Scatter(
                    x=df_slice.index,
                    y=[df_slice["Close"].min()] * len(df_slice),
                    mode="lines",
                    line=dict(color="rgba(0,0,0,0)"),
                    showlegend=False
                ), secondary_y=False)

                # ---------------------------------------
                # 2. Filled price line
                # ---------------------------------------
                fig.add_trace(go.Scatter(
                    x=df_slice.index,
                    y=df_slice["Close"],
                    mode="lines",
                    name="Sector Index",
                    fill='tonexty',   # <-- fills to baseline, not zero
                    fillcolor='rgba(214,235,255,0.5)',
                    line=dict(color='#78afd9', width=2)
                ), secondary_y=False)

                # ---------------------------------------
                # 3. Pulse (DPCM_q) line
                # ---------------------------------------
                fig.add_trace(go.Scatter(
                    x=df_slice.index,
                    y=df_slice["DPCM_q"],
                    mode="lines",
                    name="DPCM",
                    line=dict(color="#78afd9", shape="hv")
                ), secondary_y=True)


            # -----------------------------
            # Apply styling
            # -----------------------------
            fig.update_layout(
                plot_bgcolor='white',
                legend=dict(orientation="h", yanchor="top", y=1.15, xanchor="right", x=1),
                height=400,
                margin=dict(l=40, r=40, t=40, b=40),
                title=f"{name} — Trend ({lookback} days, {mode}): {direction}"
            )

            fig.update_xaxes(showgrid=True, gridcolor="lightgrey")
            fig.update_yaxes(showgrid=True, gridcolor="lightgrey")

            graphs.append(html.Div([dcc.Graph(figure=fig)], style={"margin-bottom": "40px"}))

        charts_output = html.Div(graphs)

    # ============================================================
    # 3. HEATMAP TAB
    # ============================================================
    heatmap_output = ""
    if active_tab == "heatmap":

        heatmap_data = {}

        for name, df in active_data.items():
            df_slice = df.tail(lookback)

            if mode == "pulse":
                series = df_slice["DPCM_q"].cumsum()

            elif mode == "weighted":
                series = df_slice["DPCM_raw"].cumsum()

            elif mode == "rsi":
                delta = df_slice["Close"].diff()
                up = delta.clip(lower=0)
                down = -delta.clip(upper=0)
                roll_up = up.ewm(span=14, adjust=False).mean()
                roll_down = down.ewm(span=14, adjust=False).mean()
                rs = roll_up / roll_down
                series = 100 - (100 / (1 + rs))
                series = (series - series.mean()) / (series.std() + 1e-9)

            elif mode == "macd":
                ema12 = df_slice["Close"].ewm(span=12, adjust=False).mean()
                ema26 = df_slice["Close"].ewm(span=26, adjust=False).mean()
                macd_line = ema12 - ema26
                signal_line = macd_line.ewm(span=9, adjust=False).mean()
                hist = macd_line - signal_line
                series = hist.rolling(5).mean()
                series = (series - series.mean()) / (series.std() + 1e-9)

            heatmap_data[name] = series

        common_index = sorted(set.intersection(*[set(s.index) for s in heatmap_data.values()]))

        aligned = {name: s.reindex(common_index).fillna(0) for name, s in heatmap_data.items()}

        heatmap_df = pd.DataFrame(aligned, index=common_index)

        heatmap_fig = go.Figure(
            data=go.Heatmap(
                z=heatmap_df.T.values,
                x=heatmap_df.index.astype(str),
                y=heatmap_df.columns,
                colorscale="RdYlGn",
                colorbar=dict(title=mode.upper()),
            )
        )

        heatmap_output = html.Div(dcc.Graph(figure=heatmap_fig))

    # ============================================================
    # 4. QUADRANT TAB
    # ============================================================
    quadrant_output = ""
    if active_tab == "quadrant":

        quad_x = []
        quad_y = []
        quad_labels = []
        quad_x_prev = []
        quad_y_prev = []

        # ---------------------------------------
        # Dynamic windows based on slider
        # ---------------------------------------
        short_window = max(3, int(lookback * 0.10))   # 10% of lookback
        long_window  = max(5, int(lookback * 0.30))   # 30% of lookback

        for name, df in active_data.items():
            df_slice = df.tail(lookback)

            # ---------------------------------------
            # Select indicator series
            # ---------------------------------------
            if mode == "pulse":
                series = df_slice["DPCM_q"]

            elif mode == "weighted":
                series = df_slice["DPCM_raw"]

            elif mode == "rsi":
                delta = df_slice["Close"].diff()
                up = delta.clip(lower=0)
                down = -delta.clip(upper=0)
                roll_up = up.ewm(span=14, adjust=False).mean()
                roll_down = down.ewm(span=14, adjust=False).mean()
                rs = roll_up / roll_down
                series = 100 - (100 / (1 + rs))

            elif mode == "macd":
                ema12 = df_slice["Close"].ewm(span=12, adjust=False).mean()
                ema26 = df_slice["Close"].ewm(span=26, adjust=False).mean()
                macd_line = ema12 - ema26
                signal_line = macd_line.ewm(span=9, adjust=False).mean()
                series = macd_line - signal_line

            # ---------------------------------------
            # Short-term momentum (dynamic)
            # ---------------------------------------
            if len(series) > short_window:
                short_mom = series.rolling(short_window).mean().iloc[-1]
                short_prev = series.rolling(short_window).mean().iloc[-2]
            else:
                short_mom = series.iloc[-1]
                short_prev = short_mom

            # ---------------------------------------
            # Long-term momentum (dynamic)
            # ---------------------------------------
            if len(series) > long_window:
                long_mom = series.rolling(long_window).mean().iloc[-1]
                long_prev = series.rolling(long_window).mean().iloc[-2]
            else:
                long_mom = series.iloc[-1]
                long_prev = long_mom

            quad_x.append(short_mom)
            quad_y.append(long_mom)
            quad_labels.append(name)
            quad_x_prev.append(short_prev)
            quad_y_prev.append(long_prev)

        # ---------------------------------------
        # Build quadrant figure
        # ---------------------------------------
        fig_q = go.Figure()

        # Colour coding
        colors = []
        for x, y in zip(quad_x, quad_y):
            if x >= 0 and y >= 0:
                colors.append("green")
            elif x < 0 and y >= 0:
                colors.append("orange")
            elif x < 0 and y < 0:
                colors.append("red")
            else:
                colors.append("blue")

        # Scatter points
        fig_q.add_trace(
            go.Scatter(
                x=quad_x,
                y=quad_y,
                mode="markers+text",
                text=quad_labels,
                textposition="top center",
                marker=dict(size=16, color=colors, line=dict(width=1, color="black")),
            )
        )

        # Arrows showing movement
        for x0, y0, x1, y1 in zip(quad_x_prev, quad_y_prev, quad_x, quad_y):
            fig_q.add_annotation(
                x=x1,
                y=y1,
                ax=x0,
                ay=y0,
                showarrow=True,
                arrowhead=3,
                arrowsize=1.2,
                arrowwidth=1.5,
                arrowcolor="black",
            )

        # Quadrant lines
        fig_q.add_shape(type="line", x0=0, x1=0, y0=min(quad_y), y1=max(quad_y), line=dict(color="grey"))
        fig_q.add_shape(type="line", x0=min(quad_x), x1=max(quad_x), y0=0, y1=0, line=dict(color="grey"))

        # Labels
        fig_q.add_annotation(x=max(quad_x)*0.7, y=max(quad_y)*0.7, text="LEADING", showarrow=False, font=dict(color="green", size=14))
        fig_q.add_annotation(x=min(quad_x)*0.7, y=max(quad_y)*0.7, text="WEAKENING", showarrow=False, font=dict(color="orange", size=14))
        fig_q.add_annotation(x=min(quad_x)*0.7, y=min(quad_y)*0.7, text="LAGGING", showarrow=False, font=dict(color="red", size=14))
        fig_q.add_annotation(x=max(quad_x)*0.7, y=min(quad_y)*0.7, text="IMPROVING", showarrow=False, font=dict(color="blue", size=14))

        fig_q.update_layout(
            title=f"Quadrant Momentum ({lookback} days, {mode.upper()})",
            xaxis_title=f"Short-Term Momentum ({short_window}-period)",
            yaxis_title=f"Long-Term Momentum ({long_window}-period)",
            height=650,
            plot_bgcolor="white",
        )

        quadrant_output = html.Div(dcc.Graph(figure=fig_q))
        
    return ranking_panel, charts_output, heatmap_output, quadrant_output



# ---------------------------------------------------------
# Core calculation functions
# ---------------------------------------------------------

def min_move_within_budget(purchase_price, target_profit, max_investment,
                           stamp_duty_rate, fee):

    best = None
    N = 1

    while True:
        buy_cost = N * purchase_price * (1 + stamp_duty_rate) + fee

        if buy_cost > max_investment:
            break

        required_sell_value = buy_cost + target_profit + fee
        required_sell_price = required_sell_value / N
        price_move = required_sell_price - purchase_price

        if price_move > 0:
            pct_move = (price_move / purchase_price) * 100

            if best is None or price_move < best["price_move"]:
                best = {
                    "shares": N,
                    "investment_required": buy_cost,
                    "required_sell_price": required_sell_price,
                    "price_move": price_move,
                    "percentage_move": pct_move,
                    "stamp_duty_rate": stamp_duty_rate,
                    "transaction_fee": fee
                }

        N += 1

    return best


# ---------------------------------------------------------
# Profit Curve (Cost Basis Adjusted)
# ---------------------------------------------------------

def generate_graphical_calculator_profit_curve(purchase_price, shares, target_profit,
                          investment, five_day_low, five_day_high,
                          stamp_duty_rate, fee):

    # Total buy cost including stamp duty + fee
    buy_cost = shares * purchase_price * (1 + stamp_duty_rate) + fee

    # Cost basis per share
    breakeven = buy_cost / shares

    # Required sell price per share
    required_sell_value = buy_cost + target_profit + fee
    required_sell_price = required_sell_value / shares

    # Correct price movement (from cost basis)
    required_price_move = required_sell_price - breakeven

    # Dynamic x-axis scaling
    max_move = max(required_price_move * 1.5, breakeven * 0.10)

    # Include negative movement so loss region is visible
    price_moves = np.linspace(-max_move * 0.6, max_move, 300)

    # Sell prices based on cost basis
    sell_prices = breakeven + price_moves

    # Profit calculation
    profits = (shares * sell_prices - fee) - buy_cost

    # Intersection point
    idx = (np.abs(profits - target_profit)).argmin()
    intersection_x = price_moves[idx]
    intersection_y = profits[idx]

    # Build figure
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[0],
        y=[0],
        mode="markers",
        marker=dict(size=12, color="dark blue"),
        name="Breakeven",
        showlegend=False
    ))

    fig.add_vline(
        x=0,
        line=dict(color="dark blue", dash="dot", width=0.5),
        name="Breakeven"
    )

    fig.add_annotation(
        x=0,
        y=profits.min(),
        text="Breakeven",
        showarrow=False,
        yshift=-25,
        font=dict(size=11, color="darkblue")
    )




    # Profit curve
    fig.add_trace(go.Scatter(
        x=price_moves,
        y=profits,
        mode='lines',
        name='Profit',
        line=dict(color="green", width=3)
    ))

    # Shaded profit region
    fig.add_hrect(
        y0=0, y1=profits.max(),
        fillcolor="green", opacity=0.08, line_width=0
    )

    # Shaded loss region
    fig.add_hrect(
        y0=profits.min(), y1=0,
        fillcolor="red", opacity=0.08, line_width=0
    )

    # Target profit line
    fig.add_hline(
        y=target_profit,
        line=dict(color='grey', dash='dash', width=0.5),
        name='Target Profit'
    )

    # Required price move line
    fig.add_vline(
        x=intersection_x,
        line=dict(color='grey', dash='dash', width=0.5),
        name='Required Price Move'
    )

    # Intersection marker + annotation
    pct_move = (intersection_x / breakeven) * 100

    fig.add_trace(go.Scatter(
        x=[intersection_x],
        y=[intersection_y],
        mode='markers+text',
        text=[(
            f"Breakeven: {breakeven:.4f}<br>"
            f"Required Sell Price: {required_sell_price:.4f}<br>"
            f"Price Move: {intersection_x:.4f} [{pct_move:.2f}%]"
        )],
        textposition="top left",
        textfont=dict(size=12),
        marker=dict(size=12, color='black'),
        showlegend=False
    ))

    # ---------------------------------------------------------
    # Add centered 5-day price band (vertical band)
    # ---------------------------------------------------------
    if five_day_low is not None and five_day_high is not None:

        x0 = five_day_low - breakeven
        x1 = five_day_high - breakeven

        fig.add_shape(
            type="rect",
            x0=x0,
            x1=x1,
            y0=profits.min(),
            y1=profits.max(),
            fillcolor="orange",
            opacity=0.25,
            line_width=0,
            layer="below"
        )

        fig.add_annotation(
            x=(x0 + x1) / 2,
            y=profits.max(),
            text="5-Day Price Movement",
            showarrow=False,
            yshift=20,
            font=dict(size=12, color="orange")
        )
        
        #5 day low text
        fig.add_annotation(
            x=x0,
            y=profits.min(),
            text=f"Low: {five_day_low:.4f}",
            showarrow=False,
            yshift=-10,
            font=dict(size=11, color="orange")
        )

        #5day High text
        fig.add_annotation(
            x=x1,
            y=profits.min(),
            text=f"High: {five_day_high:.4f}",
            showarrow=False,
            yshift=-10,
            font=dict(size=11, color="orange")
        )


    # Axis scaling
    fig.update_xaxes(range=[
        price_moves.min() * 1.1,
        price_moves.max() * 1.1
    ])

    y_range = profits.max() - profits.min()
    fig.update_yaxes(range=[
        profits.min() - y_range * 0.25,
        profits.max() + y_range * 0.25
    ])

    fig.update_layout(
        title="Profit vs Price Movement (Cost Basis Adjusted)",
        xaxis_title="Price Movement ()",
        yaxis_title="Profit",
        template="plotly_white",
        height=465
    )

    return fig


# ---------------------------------------------------------
# Graphical Calculator
# ---------------------------------------------------------

def update_graphical_calculator(stock_symbol, purchase_price, desired_profit, max_investment, taxes, trading_fees):
    
    target_profit = float(desired_profit)

    # Fetch last 5 days of stock data
    try:
        data = yf.Ticker(stock_symbol).history(period="5d")
        if data.empty:
            five_day_low = None
            five_day_high = None
            last_close_price = None
        else:
            five_day_low = data["Low"].min()
            five_day_high = data["High"].max()
            last_close_price = data['Close'].iloc[-1]
            # DO NOT override purchase_price
    except Exception:
        five_day_low = None
        five_day_high = None
        last_close_price = None


    result = min_move_within_budget(purchase_price, target_profit, max_investment, taxes, trading_fees)

    if result is None:
        fig = go.Figure()
        fig.add_annotation(
            text="No valid share count fits within the investment budget.",
            x=0.5, y=0.5, showarrow=False
        )
        return fig, ""

    # Compute breakeven for summary
    breakeven = (result["investment_required"] / result["shares"])
    profit_loss = ((last_close_price - breakeven) *  result["shares"]) - result["transaction_fee"]


    x0 = five_day_low - breakeven if five_day_low else None
    x1 = five_day_high - breakeven if five_day_high else None



    fig = generate_graphical_calculator_profit_curve(
        purchase_price,
        result["shares"],
        target_profit,
        result["investment_required"],
        five_day_low,
        five_day_high,
        taxes, 
        trading_fees
    )

    return fig






if __name__ == "__main__":
    app.run(debug=True)
    