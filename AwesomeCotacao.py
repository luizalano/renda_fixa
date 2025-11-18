import requests
import json
from databasefunctions import *

class AwesomeCotacao:
    def __init__(self):
        self.getConexao()

    def getConexao(self):
        try:
            self.conexao = ConectaBD.retornaConexao()
            self.cursor = self.conexao.cursor()
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")

    def _busca_moeda(self, url, idmoeda):
        """Busca cotação na API e grava no banco"""
        response = requests.get(url)

        if response.status_code == 200:
            dados = response.json()
            if dados:
                ultima_cotacao = dados[0]  # Última cotação disponível
                data_cotacao = ultima_cotacao["create_date"][:10]  # Formato 'YYYY-MM-DD'
                valor_cotacao = float(ultima_cotacao["bid"])  # Preço de venda

                self._grava_cotacao(idmoeda, data_cotacao, valor_cotacao)
            else:
                print("Nenhuma cotação encontrada.")
        else:
            print(f"Erro ao acessar API: {response.status_code}")

    def _grava_cotacao(self, idmoeda, data_cotacao, valor_cotacao):
        """Insere ou atualiza a cotação no banco"""
        sql_verifica = f"SELECT id FROM cotacao WHERE idmoeda = {idmoeda} AND datacotacao = '{data_cotacao}'"
        resultado = self.cursor.execute(sql_verifica)

        try:
            if resultado:
                sql_update = f"UPDATE cotacao SET valorcotacao = {valor_cotacao} WHERE idmoeda = {idmoeda} AND datacotacao = '{data_cotacao}'"
                self.cursor.execute(sql_update)
            else:
                sql_insert = f"INSERT INTO cotacao (idmoeda, datacotacao, valorcotacao) VALUES ({idmoeda}, '{data_cotacao}', {valor_cotacao})"
                self.cursor.execute(sql_insert)
            self.conexao.commit()
        except:
            a = 9


    def busca_dollar(self):
        """Busca cotação do Dólar"""
        self._busca_moeda("https://economia.awesomeapi.com.br/json/daily/USD-BRL/1", 1)

    def busca_euro(self):
        """Busca cotação do Euro"""
        self._busca_moeda("https://economia.awesomeapi.com.br/json/daily/EUR-BRL/1", 3)


# 🔹 Exemplo de uso
if __name__ == "__main__":
    cotacao = AwesomeCotacao()
    cotacao.busca_dollar()
    cotacao.busca_euro()
