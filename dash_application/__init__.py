import sqlite3
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

conn = sqlite3.connect('trades.db')

df = pd.read_sql_query("SELECT * FROM trade INNER JOIN estrategia ON trade.MAGIC = estrategia.MAGIC", conn)
df['TOTAL_EQUITY'] = df['PROFIT'].cumsum()
#print(df)

#crio variável para ser lista de estratégias com base na coluna ESTRATEGIA do DF
opcoes = list(df['ESTRATEGIA'].unique())
opcoes.append('Todas')
opcoes.append('Carteira Win')


def create_dash_application(flask_app): #crio função que cria aplicação dash recebendo flask_app

    #dou nome à aplicação dash que vai ser criada e passo uri de acesso
    dash_app = Dash(server=flask_app, name="Dashboard", url_base_pathname="/app/resultados/")


#######CONTEUDO HTML DA APLICAÇÃO DASH###################################################

    dash_app.layout = html.Div(children=[  #todo o layout dash fica em uma Div html

        # H1
        html.H1(children='Orion Trade Manager'),

        # Div com texto
        html.Div(children=''' 
            Escolha uma estratégia para exibir os resultados.
        '''),

        html.Div(children=[
            # cria componente dropdown (lista de seleção)
            dcc.Dropdown(opcoes, value='Todas', id='lista-magic'),
        ], style={"width": "30%"}),

        dcc.Graph(  # cria gráfico dash
            id='grafico-trades',
            figure=px.line(df, x="DATE", y="TOTAL_EQUITY")
        ),

        html.H3(id='txt-profit-factor'),
        html.H3(id='txt-trades'),
        html.H3(id='txt-acerto'),
    ])

    @dash_app.callback(
        Output('grafico-trades', 'figure'),
        Input('lista-magic', 'value')
    )
    def atualiza_grafico(value):
        if value == 'Todas':

            fig = px.line(df, x="DATE", y="TOTAL_EQUITY")

            fig.update_layout(xaxis=dict(showgrid=False),
                              yaxis=dict(zeroline=False, showgrid=False),
                              )

        else:
            df_filtrada = df.loc[df['ESTRATEGIA'] == value]
            df_filtrada['EQUITY_MAGIC'] = df_filtrada['PROFIT'].cumsum()

            fig = px.line(df_filtrada, x="DATE", y="EQUITY_MAGIC")

            fig.update_layout(xaxis=dict(showgrid=False),
                              yaxis=dict(zeroline=False, showgrid=False),
                              )
        return fig

    @dash_app.callback(
        Output('txt-profit-factor', 'children'),
        Input('lista-magic', 'value')
    )
    def atualiza_profit_factor(value):
        if value == 'Todas':
            df_lucros = df.loc[df['PROFIT'] > 0]
            lucros = df_lucros['PROFIT'].sum()
            df_perdas = df.loc[df['PROFIT'] < 0]
            perdas = df_perdas['PROFIT'].sum()
            profit_factor = round(abs(lucros / perdas), 2)
        else:
            df_filtrada = df.loc[df['ESTRATEGIA'] == value]
            df_lucros = df_filtrada.loc[df_filtrada['PROFIT'] > 0]
            lucros = df_lucros['PROFIT'].sum()
            df_perdas = df_filtrada.loc[df_filtrada['PROFIT'] < 0]
            perdas = df_perdas['PROFIT'].sum()
            profit_factor = round(abs(lucros / perdas), 2)
        return f'Profit Factor: {profit_factor}'

    @dash_app.callback(
        Output('txt-trades', 'children'),
        Input('lista-magic', 'value')
    )
    def atualiza_num_trades(value):
        if value == 'Todas':
            num_trades = df['PROFIT'].count()
        else:
            df_filtrada = df.loc[df['ESTRATEGIA'] == value]
            num_trades = df_filtrada['PROFIT'].count()
        return f'Nº Trades: {num_trades}'

    return dash_app


def salvaDados():
    # importa e formata df trades
    df = pd.read_csv('assets/historico_trades_conta.csv')
    df_saidas = df.loc[df['ENTRY'] == 1]
    df_saidas.drop('ENTRY', axis=1, inplace=True)
    df_saidas.drop('FEE', axis=1, inplace=True)
    df_saidas.drop('SWAP', axis=1, inplace=True)
    df_saidas['TYPE'].replace({0: 'buy'}, inplace=True)
    df_saidas['TYPE'].replace({1: 'sell'}, inplace=True)

    # importa e formata df estrategias
    df_estrategias = pd.read_csv('assets/estrategia_magic_number.csv', sep=';')
    df_estrategias
    #print(df_saidas)

    # cria conexão, banco e tabela sqlite
    conn = sqlite3.connect('trades.db')

    # insere DFs pandas no banco de dados com método pandas
    df_saidas.to_sql(name="trade", con=conn, if_exists='replace', index=True)
    df_estrategias.to_sql(name="estrategia", con=conn, if_exists='replace', index=True)