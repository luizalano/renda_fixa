import requests
import json
from dataBaseFunctionMG import *

class AwesomeCotacao:
    def __init__(self):
        self.getConexao()

    def getConexao(self):
        """Abre conexão com o banco"""
        fileSettings = open(".\\settings.cfg", )
        dataSettings = json.load(fileSettings)
        self.conexao = ConMG(dataSettings)
        if self.conexao.con is None:
            sys.exit()

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
        resultado = self.conexao.executaSelect(sql_verifica)

        try:
            if resultado:
                sql_update = f"UPDATE cotacao SET valorcotacao = {valor_cotacao} WHERE idmoeda = {idmoeda} AND datacotacao = '{data_cotacao}'"
                self.conexao.executaSQL(sql_update)
                #print(f"✅ Cotação {idmoeda} ATUALIZADA para {valor_cotacao} em {data_cotacao}.")
            else:
                sql_insert = f"INSERT INTO cotacao (idmoeda, datacotacao, valorcotacao) VALUES ({idmoeda}, '{data_cotacao}', {valor_cotacao})"
                self.conexao.executaSQL(sql_insert)
                #print(f"✅ Cotação {idmoeda} INSERIDA: {valor_cotacao} em {data_cotacao}.")
            self.conexao.con.commit()
        except:
            self.conexao.con.close()


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
