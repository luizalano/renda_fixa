# coding: utf-8


import datetime
from diversos import *
from datetime import date
from databasefunctions import *
import yfinance as yf


class BuscaCotacaoBolsas():

    idativo = -1
    datacotacao = None
    preco = 0.0
    erros = 0
    zeros = 0
    ativos = 0
    idBolsa = None
    siglaBolsa = None

    def __init__(self):

        self.hoje = date.today()
        self.dia = self.hoje

    def getConexao(self):
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def busca_em_todas(self, data):
        self.realiza_busca('B3', data)
        self.realiza_busca('NYSE', data)
        self.realiza_busca('NASDAQ', data)

    def realiza_busca(self, siglabolsa, qualdia):
        if qualdia:
            self.dia = datetime.strptime(qualdia, "%Y-%m-%d").date()
        else:
            self.dia = self.hoje
        if self.eh_Feriado(self.dia.strftime("%Y-%m-%d"), siglabolsa):
            print('Em feriado não tem pregão!')
        else:
            if self.dia.weekday() < 5: # Não roda nos finais de semana
                self.siglaBolsa = siglabolsa
                self.conexao = None
                self.listaAtivos = self.busca_lista_de_ativos_de_interesse()
                self.busca_precos_de_fechamento()
            else:
                print('Fim de semana não tem pregão!')

    def eh_Feriado(self, dia, bolsa):
        conexao = self.getConexao()

        clausulaSql = 'select dia from feriado where dia = %s and idbolsa = (select id from bolsa where sigla = %s);'
        lista = None
        with conexao.cursor() as cursor:
            cursor.execute(clausulaSql, (dia, bolsa))
            lista = cursor.fetchone()
            if lista: return True
            else: return False
        
        conexao.close() 

    def busca_lista_de_ativos_de_interesse(self):
        conexao = self.getConexao()

        clausulaSql = 'select id, sigla from bolsa where sigla = %s;'
        
        list = None
        self.idBolsa = None

        with conexao.cursor() as cursor:
            cursor.execute(clausulaSql, (self.siglaBolsa, ))
            lista = cursor.fetchone()

        if lista:
            self.idBolsa = lista[0]

            clausulaSql = 'select id, sigla, razaosocial, interesse from ativo where interesse = 1 and idbolsa = %s order by sigla;'

            with conexao.cursor() as cursor:
                cursor.execute(clausulaSql, (self.idBolsa, ))
                return cursor.fetchall()
        conexao.close()

    def salva(self):
        clausulaSql = '''
            INSERT INTO cotacaoativo (idativo, datacotacao, preco, maximo, minimo)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (idativo, datacotacao) DO UPDATE
            SET preco = EXCLUDED.preco,
                maximo = EXCLUDED.maximo,
                minimo = EXCLUDED.minimo;
        '''

        with self.conexao.cursor() as cursor:
            try:
                cursor.execute("SAVEPOINT before_insert")
                cursor.execute(clausulaSql, (int(self.idativo), self.datacotacao, float(self.preco), float(self.maxima), float(self.minima)))
            except Exception as e:
                cursor.execute("ROLLBACK TO SAVEPOINT before_insert")
                print(f"Erro ao salvar cotação: {e}")
                self.erros += 1
            finally:
                cursor.execute("RELEASE SAVEPOINT before_insert")

    def busca_precos_de_fechamento(self):
        self.conexao = self.getConexao()    
        for row in self.listaAtivos:
            self.ativos += 1
            self.idativo = row[0]
            sigla = row[1]
            #idbolsa = row[4]  # <-- certifique-se de que a consulta SQL traga idbolsa também
            self.datacotacao = self.dia

            sufixo = self.get_sufixo_bolsa(self.siglaBolsa)

            cotacao = self.get_cotacao_por_data(sigla, self.dia, sufixo=sufixo)

            if cotacao:
                self.preco = cotacao["fechamento"]
                self.maxima = cotacao["maxima"]
                self.minima = cotacao["minima"]
                self.salva()
            else:
                self.zeros += 1

        self.conexao.commit()
        self.conexao.close()

    def get_cotacao_por_data(self, arg, data, sufixo):
        """ Obtém a cotação do ativo para uma data específica usando Yahoo Finance """
        sigla = str(arg).upper() + str(sufixo).upper()
        data_inicio = data
        data_fim = data_inicio + timedelta(days=1)
        data_str_inicio = data_inicio.strftime("%Y-%m-%d")
        data_str_fim = data_fim.strftime("%Y-%m-%d")
        try:
            ativo = yf.Ticker(sigla)
            cotacoes = ativo.history(start=data_str_inicio, end=data_str_fim)

            if not cotacoes.empty:
                return {
                    "fechamento": cotacoes["Close"].iloc[-1],
                    "maxima": cotacoes["High"].iloc[-1],
                    "minima": cotacoes["Low"].iloc[-1]
                }
            else:
                print(f"⚠️ Nenhuma cotação disponível para {sigla} em {data_str_inicio}")
                return None

        except Exception as e:
            print(f"❌ Erro ao obter cotação para {sigla}: {e}")
            return None

    def get_sufixo_bolsa(self, siglaBolsa):
        if siglaBolsa == 'B3': 
            return ".SA"
        elif siglaBolsa == 'NASDAQ':
            return ""  # ticker puro
        elif siglaBolsa == 'NYSE': 
            return ""  # ticker puro
        elif siglaBolsa == 'MILAN':
            return ".MI"
        else:
            return ""



def main():
    app = wx.App()
    objeto = BuscaCotacaoBolsas()
    app.MainLoop()
    objeto.busca_em_todas(None)

    print('Em todas as bolsas...')
    print("Quantos Ativos de interesse = " + str(objeto.ativos))
    print("Erros de inserção = "  + str(objeto.erros))
    print("Erros de cotação = " + str(objeto.zeros))


if __name__ == '__main__':
    main()
