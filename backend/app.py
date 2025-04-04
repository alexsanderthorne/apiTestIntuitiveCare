# backend/app.py
import pandas as pd
from flask import Flask, jsonify, abort
from flask_cors import CORS
import os

# Verifica a codificação comum para arquivos CSV brasileiros
def read_csv_with_encoding(filepath):
    encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1']
    for enc in encodings_to_try:
        try:
            print(f"Tentando ler CSV com codificação: {enc}")
            df = pd.read_csv(filepath, sep=';', encoding=enc, low_memory=False)
            print(f"CSV lido com sucesso usando {enc}.")
            return df
        except UnicodeDecodeError:
            print(f"Falha ao decodificar com {enc}.")
        except Exception as e:
            print(f"Erro inesperado ao ler com {enc}: {e}")
            # Se não for erro de decodificação, talvez o problema seja outro
            # Pode ser útil relançar a exceção ou retornar None/abortar aqui
            # raise e # Descomente se quiser que outros erros parem a execução
    print("Erro: Não foi possível ler o arquivo CSV com as codificações testadas.")
    return None

app = Flask(__name__)
# Habilita CORS para permitir requisições do frontend (que roda em outra porta)
CORS(app)

# Define o caminho para o arquivo CSV
# __file__ é o caminho do script app.py
# os.path.dirname obtém o diretório onde o script está
# os.path.join junta o diretório com o nome do arquivo CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(BASE_DIR, 'relatorio_operadoras_ativas.csv')

# Cache simples para os dados (para não ler o CSV a cada requisição)
operadoras_data = None

@app.route('/api/operadoras', methods=['GET'])
def get_operadoras():
    global operadoras_data

    # Se os dados ainda não foram carregados, leia o arquivo
    if operadoras_data is None:
        print(f"Tentando carregar dados do CSV: {CSV_FILE_PATH}")
        if not os.path.exists(CSV_FILE_PATH):
            print(f"Erro: Arquivo CSV não encontrado em {CSV_FILE_PATH}")
            # Retorna 404 Not Found se o arquivo não existe
            abort(404, description="Arquivo CSV não encontrado no servidor.")

        try:
            # Use a função que tenta diferentes codificações
            df = read_csv_with_encoding(CSV_FILE_PATH)

            if df is None:
                 # Se read_csv_with_encoding retornou None, houve um problema na leitura
                 abort(500, description="Falha ao ler ou decodificar o arquivo CSV.")

            # Limpeza básica: remover linhas onde colunas essenciais são NaN (opcional)
            # Ajuste 'Registro ANS' para o nome exato da coluna no seu CSV
            # Verifique as colunas importantes do seu CSV
            # df.dropna(subset=['Registro ANS', 'Razão Social'], inplace=True)

            # Converte valores NaN para None (que vira null em JSON)
            df = df.where(pd.notnull(df), None)

            # Converte o DataFrame para uma lista de dicionários
            operadoras_data = df.to_dict(orient='records')
            print(f"Dados carregados com sucesso. {len(operadoras_data)} registros.")

        except FileNotFoundError:
             print(f"Erro Crítico: Arquivo CSV não encontrado em {CSV_FILE_PATH}")
             abort(404, description="Arquivo CSV não encontrado.")
        except pd.errors.EmptyDataError:
             print(f"Erro: Arquivo CSV está vazio: {CSV_FILE_PATH}")
             abort(500, description="Arquivo CSV está vazio.")
        except Exception as e:
            # Captura outros erros possíveis durante a leitura/processamento do Pandas
            print(f"Erro ao processar o arquivo CSV: {e}")
            abort(500, description=f"Erro interno ao processar dados: {e}")

    # Retorna os dados em formato JSON
    return jsonify(operadoras_data)

# Rota para verificar se o servidor está rodando
@app.route('/')
def index():
    return "Servidor Flask para API de Operadoras ANS está rodando!"

if __name__ == '__main__':
    # Roda o servidor Flask na porta 5000 (padrão)
    # debug=True recarrega o servidor automaticamente quando o código muda (bom para desenvolvimento)
    app.run(debug=True, host='0.0.0.0', port=5001)