import requests
import json
from databasefunctions import *
from diversos import *
from datetime import *  

class AwesomeCotacao:

    def getConexao(self):
        try:
            conexao = ConectaBD.retornaConexao()
            return conexao
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return None
        
    def _busca_moeda(self, url, idmoeda):
        """Busca cotação na API e grava no banco"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                dados = response.json()
                if dados:
                    ultima_cotacao = dados[0]  # Última cotação disponível
                    data_cotacao = ultima_cotacao["create_date"][:10]  # Formato 'YYYY-MM-DD'
                
                    valor_cotacao = float(ultima_cotacao["bid"])  # Preço de venda

                    self.grava_cotacao(idmoeda, data_cotacao, valor_cotacao)
                else:
                    print("Nenhuma cotação encontrada.")
            else:
                print(f"Erro ao acessar API: {response.status_code}")
        except Exception as e:
            print(f"Erro ao processar dados da API: {e}")

    def grava_cotacao(self, idmoeda, data_cot, valor_cotacao):
        """Insere ou atualiza a cotação no banco"""
        conexao = self.getConexao()
        cursor = conexao.cursor()
        data_cotacao = devolveDate(data_cot)
        #sql_verifica = f"SELECT id FROM cotacao WHERE idmoeda = {idmoeda} AND datacotacao = '{data_cotacao}'"
        cursor.execute("SELECT id FROM cotacao WHERE idmoeda = %s AND datacotacao = %s", (idmoeda, data_cotacao))
        resultado = cursor.fetchone()

        try:
            if resultado:
                sql_update = f"UPDATE cotacao SET valorcotacao = {valor_cotacao} WHERE idmoeda = {idmoeda} AND datacotacao = '{data_cotacao}'"
                cursor.execute(sql_update)
            else:
                sql_insert = f"INSERT INTO cotacao (idmoeda, datacotacao, valorcotacao) VALUES ({idmoeda}, '{data_cotacao}', {valor_cotacao})"
                cursor.execute(sql_insert)
            conexao.commit()
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
