from flask import Flask, render_template # importa classe Flask da biblioteca flask
import sqlite3
import pandas as pd
from dash_application import create_dash_application
pd.options.mode.chained_assignment = None  # default='warn'

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

salvaDados() #chamo função para salvar dados

#criando aplicação Flask
app = Flask(__name__)

create_dash_application(app) #chamo função da aplicação dash que foi importada

@app.route("/app/") #função que inicializa a aplicação Flask e chama função de salvar dados csv no banco e retorna página HTML
def resultados():

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug= False, host='0.0.0.0')
