import dash
from dash import html, dcc
from dash_auth import BasicAuth
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
 
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from dash_bootstrap_templates import load_figure_template

load_figure_template("minty")

app = dash.Dash(external_stylesheets=[dbc.themes.MORPH])
USER_PWD = { "usuario": "cousin"}
BasicAuth(app,USER_PWD)
server = app.server

df_cheque = pd.read_excel('Assets/Projeto Cousin.xlsx',sheet_name = 1)
df_cartao = pd.read_excel('Assets/Projeto Cousin.xlsx',sheet_name = 2)

df_cheque["data_entrada"] = pd.to_datetime(df_cheque["Vencimento"])
df_cheque['origem'] = 'Cheque'
df_cheque['destino'] = 'Entrada'
df_cheque['valor'] = df_cheque['Valor']

df_cartao["data_entrada"] = pd.to_datetime(df_cartao["Data Operação"])
df_cartao['origem'] = 'Cartão'
df_cartao['destino'] = 'Entrada'
df_cartao['valor'] = df_cartao['Vlr.Líquido(R$)']

df_union = pd.concat([df_cartao[['data_entrada','valor','origem','destino']], df_cheque[['data_entrada','valor','origem','destino']]], ignore_index=True)
df_union = df_union.dropna()

df_union['Ano'] = df_union['data_entrada'].dt.year 
df_union['Mes'] = df_union['data_entrada'].dt.month
df_union = df_union[df_union['Ano'] >= 2023]
df_union['AnoMes'] = df_union['Ano'].astype(str) + '-' + df_union['Mes'].astype(str).str.zfill(2)

# df_grouped = df_union.groupby(['Ano', 'Mes','origem'], as_index=False)['valor'].sum()
# df_grouped['AnoMes'] = df_grouped['Ano'].astype(str) + '-' + df_grouped['Mes'].astype(str).str.zfill(2)

# fig = px.bar(df_grouped, x='AnoMes', y='valor', color='origem', barmode='group', 
#              labels={'AnoMes': 'Ano-Mês', 'Valor': 'Saldo'}, title='Soma da Coluna "Valor" por Ano e Mês')

# fig.show()

app.layout = html.Div(id='div1',
    children=[
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H2("Cousin Woman - Gerencial"),
                    html.Hr(),
                    html.H5("Origem"),
                    dcc.Checklist(df_union.origem.value_counts().index,df_union.origem.value_counts().index,
                    id= "origem",inputStyle={"margin-right": "5px", "margin-left": "20px"}),

                    html.H5("Mês"),
                    dcc.Dropdown(df_union.AnoMes.value_counts().index,df_union.AnoMes.value_counts().index,
                    id= "anomes")#,inputStyle={"margin-right": "5px", "margin-left": "20px"})
                    ], style={"height": "100vh", "margin": "20px", "padding": "20px"})
            ],sm=3),

            dbc.Col([
                dbc.Row([
                    dcc.Graph(id="grafico_area")
                    ]),

                dbc.Row([
                    dcc.Graph(id="grafico_2")
                    ])
            ],sm=9)
        ])
    ]                                           
)

#------CALLBACKS-----------------------------------------------------------------------------------------
@app.callback(
            Output("grafico_area","figure"),
            Output("grafico_2","figure"),
            [
                Input("origem", "value"),
                Input("anomes", "value")
            ])

def render_graphs(origem,anomes):
    operacao = np.sum
    #anomes = "Impostos"
    df_filter = df_union[df_union["origem"].isin(origem)]
    df_filter = df_filter[df_filter["AnoMes"].isin(anomes)]
    
    df_graf1 = df_filter.groupby(['AnoMes','origem'], as_index=False)['valor'].sum()
    df_graf2 = df_cartao.groupby(['Condição','origem'],as_index=False)['valor'].sum()

    fig1 = px.bar(df_graf1, x='AnoMes', y='valor', color='origem', barmode='group', 
             labels={'AnoMes': 'Ano-Mês', 'Valor': 'Saldo'}, title='Receita Recebida - Origem')
    #fig.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=200, template="minty")
    fig1.update_layout( plot_bgcolor='rgba(0,0,0,0)', # Remove a tela de fundo 
                      paper_bgcolor='rgba(0,0,0,0)', # Remove a cor de fundo do papel 
                      font=dict(color='black')) # Define a cor dos labels

    fig2 = px.bar(df_graf2, x='Condição', y='valor', color='origem', 
             labels={'Condição': 'Condição', 'Valor': 'Valor'}, title='Valores parcelados')
    #fig.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=200, template="minty")
    fig2.update_layout( plot_bgcolor='rgba(0,0,0,0)', # Remove a tela de fundo 
                      paper_bgcolor='rgba(0,0,0,0)', # Remove a cor de fundo do papel 
                      font=dict(color='black')) # Define a cor dos labels

    return fig1, fig2


# =========  Run server  =========== #
if __name__ == "__main__":
    app.run_server(debug=False)