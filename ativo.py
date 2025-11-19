# coding: utf-8
# linha pra nada
import datetime

from diversos import *
from datetime import date
from databasefunctions import *
import yfinance as yf

class Ativo():
    id_ativo = -1
    id_conta = -1
    razao_social = ''
    sigla = ''
    lan = []
    proventos = []
    listaAtivos = []
    listaRendaAcoes = []
    listaRendaProventos = []
    listaRendaDespesas = []

    tamrazao_social = 0
    tamsigla = 0


    def __init__(self):

        self.nome_base = ConectaBD.mc_retorna_nome_base()
        self.defineTamanhos()

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def defineTamanhos(self):
        self.tamrazao_social = self.sqlBuscaTamanho('razaosocial')
        self.tamsigla = self.sqlBuscaTamanho('sigla')

    def getAll(self):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        clausulaSql = 'select a.id, a.razaosocial, a.sigla ' \
                      'from ativo as a ' \
                      'order by a.sigla;'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativos', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        lista = cursor.fetchone()
        
        self.conexao.close()

        return lista

    def buscaAtivosNegociados(self, idconta):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        if idconta > -1:
            clausulaSql = 'select distinct idativo from ativonegociado where idconta =' \
                      ' ' + str(idconta) + ';'
        else :
            clausulaSql = 'select distinct idativo from ativonegociado;'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao buscar ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.listaAtivos = []

        self.listaAtivos = row = cursor.fetchall()

        self.conexao.close()

    def clearAtivo(self):
        self.setid_ativo(-1)
        self.setrazao_social('')
        self.setsigla('')

    def insereOperacao(self, argsiglaativo, dataoperacao: date, operacao: int, valoroperacao: float, qtdeoperacao: int, idconta: int, **kwargs):

        retorno = True
        try:
            simulado = False
            if len(kwargs) > 0:
                if 'simulado' in kwargs:
                    simulado = kwargs['simulado']

            self.conexao = self.getConexao()
            cursor = self.conexao.cursor()
            # Verificar se o ativo existe na tabela 'ativo'
            cursor.execute("SELECT id FROM ativo WHERE upper(sigla) = upper(%s);", (argsiglaativo,))
            resultado = cursor.fetchone()

            idativo = resultado[0]

            # Inserir os dados na tabela 'operacao'
            insert_query = """
                INSERT INTO ativonegociado (idativo, operacao, valoroperacao, qtdeoperacao, dataoperacao, idconta, simulado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (idativo, operacao, valoroperacao, qtdeoperacao, dataoperacao, idconta, simulado))

        except Exception as e:
            retorno = False

        finally:
            self.conexao.commit()
            self.conexao.close()
            return retorno

    def updateOperacao(self, argsiglaativo, dataoperacao: date, operacao: int, valoroperacao: float, qtdeoperacao: int, idconta: int, id, **kwargs):

        retorno = True
        try:
            if len(kwargs) > 0:
                simulado = False
                if 'simulado' in kwargs:
                    simulado = kwargs['simulado']

            self.conexao = self.getConexao()
            cursor = self.conexao.cursor()
            # Verificar se o ativo existe na tabela 'ativo'
            cursor.execute("SELECT id FROM ativo WHERE upper(sigla) = upper(%s);", (argsiglaativo,))
            resultado = cursor.fetchone()

            idativo = resultado[0]

            # Inserir os dados na tabela 'operacao'
            insert_query = """
                update ativonegociado set idativo = %s, operacao = %s, valoroperacao = %s, qtdeoperacao = %s,
                dataoperacao = %s, idconta = %s, simulado = %s where id = %s;
            """
            cursor.execute(insert_query, (idativo, operacao, valoroperacao, qtdeoperacao, dataoperacao, idconta, simulado, id))

        except Exception as e:
            retorno = False

        finally:
            self.conexao.commit()
            self.conexao.close()
            return retorno

    def efetiva_lancamento_simulado(self, id):
        
        retorno = True
        try:
            self.conexao = self.getConexao
            cursor = self.conexao.cursor()
            # Inserir os dados na tabela 'operacao'
            insert_query = "update ativonegociado set simulado = False where id = %s;"
            cursor.execute(insert_query, (id,))

        except Exception as e:
            retorno = False

        finally:
            self.conexao.commit()
            self.conexao.close()
            return retorno

    def deleteOperacao(self, id):

        retorno = True
        try:
            self.conexao = self.getConexao()
            cursor = self.conexao.cursor()
            insert_query = """
                delete from ativonegociado where id = %s 
            """
            cursor.execute(insert_query, (id,))

        except Exception as e:
            retorno = False

        finally:
            self.conexao.commit()
            self.conexao.close()
            return retorno

    def insereProvento(self, argsiglaativo, dataoperacao: date, tipoprovento, proventoBruto: float, pago, proventoIR: float, idconta: int):

        retorno = True
        try:
            self.conexao = self.getConexao()
            cursor = self.conexao.cursor()
            # Verificar se o ativo existe na tabela 'ativo'
            cursor.execute("SELECT id FROM ativo WHERE upper(sigla) = upper(%s);", (argsiglaativo,))
            resultado = cursor.fetchone()

            idativo = resultado[0]

            # Inserir os dados na tabela 'operacao'
            insert_query = """
                INSERT INTO proventos (idativo, datarecebimento, valorbruto, valorir, pago, idtipoprovento, idconta)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (idativo, dataoperacao, proventoBruto, proventoIR, True, tipoprovento, idconta))

        except Exception as e:
            retorno = False

        finally:
            self.conexao.commit()
            self.conexao.close()
            return retorno

    def busca_proventos_do_ativo(self, idconta, pago):

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()
        if idconta >= 0:
            clausulaSql = 'select p.id, p.datarecebimento as "datar", ' \
                      '(p.valorbruto - p.valorir) as "valor", ' \
                      'tp.nometipoprovento as "provento", p.pago  ' \
                      'from proventos as p join  tipoprovento as tp on tp.id = p.idtipoprovento ' \
                      'where p.idativo = ' + str(self.id_ativo) + ' and ' \
                      'p.idconta = ' + str(idconta) + ';'
        else:
            clausulaSql = 'select p.id, p.datarecebimento as "datar", ' \
                      '(p.valorbruto - p.valorir) as "valor", ' \
                      'tp.nometipoprovento as "provento", p.pago  ' \
                      'from proventos as p join  tipoprovento as tp on tp.id = p.idtipoprovento ' \
                      'where p.idativo = ' + str(self.id_ativo) + ';'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler proventos!', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        row = cursor.fetchone()
        self.proventos.clear()
        while row != None:
            if pago and row[4]:
                self.proventos.append([row[0], row[1], row[2], row[3], row[4]])
            else:
                self.proventos.append([row[0], row[1], row[2], row[3], row[4]])
            row = cursor.fetchone()

        self.conexao.close()

    def buscaTiposDeProventos(self):

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()
        clausulaSql = 'select id, nometipoprovento from tipoprovento order by id;'

        lista = []
        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler tipos de proventos!', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        lista = cursor.fetchall()

        self.conexao.close()

        return lista

    def buscaIdTipoDeProvento(self, arg):

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        clausulaSql = 'select id from tipoprovento where upper(nometipoprovento) ' \
                      '= upper(\''  + arg + '\');'

        retorno = (-1)
        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler tipos de proventos!', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        row = cursor.fetchone()

        if row != None:
            retorno = row[0]

        self.conexao.close()

        return retorno

    def populaAtivoBySigla(self, arg):
        clausulaSql = 'select a.id, a.razaosocial, a.sigla ' \
                      'from ativo as a ' \
                      'where upper(a.sigla) = upper(\'' + str(arg) + '\');'

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()
        
        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativo <' + str(arg) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        row = cursor.fetchone()
        self.clearAtivo()
        if row != None:
            self.setid_ativo(row[0])
            self.setsigla(row[2])
            self.setrazao_social(row[1])

        #self.setlan(-1)

        self.conexao.close()

    def populaAtivoById(self, arg):
        clausulaSql = 'select a.id, a.razaosocial, a.sigla ' \
                      'from ativo as a ' \
                      'where a.id = ' + str(arg) + ';'

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativo <' + str(arg) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        row = cursor.fetchone()
        self.clearAtivo()
        if row != None:
            self.setid_ativo(row[0])
            self.setrazao_social(row[1])
            self.setsigla(row[2])

        #self.setlan(-1)

        self.conexao.close()


    def existeAtivo(self, arg):
        clausulaSql = 'select a.id, a.razaosocial, a.sigla ' \
                      'from ativo as a ' \
                      'where upper(a.sigla) = upper(\'' + str(arg) + '\');'

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()
        retorno = False
        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativo <' + str(arg) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        row = cursor.fetchone()
        self.clearAtivo()
        if row != None:
            retorno = True

        self.conexao.close()

        return retorno

    def setlan(self, idconta):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()
        self.lan.clear()

        if idconta == (-1):
            clausulaSql = 'select a.id, a.dataoperacao, a.operacao, a.qtdeoperacao, a.valoroperacao, a.simulado  ' \
                      'from ativonegociado as a ' \
                      'where a.idativo = ' + str(self.id_ativo) +  ' '\
                      'order by a.dataoperacao, a.ordemdia, a.id;'
        else:
            clausulaSql = 'select a.id, a.dataoperacao, a.operacao, a.qtdeoperacao, a.valoroperacao, a.simulado  ' \
                          'from ativonegociado as a ' \
                          'where a.idativo = ' + str(self.id_ativo) + ' ' \
                          'and a.idconta = ' + str(idconta) + ' ' \
                          'order by a.dataoperacao, a.ordemdia, a.id;'
        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.lan = []

        row = cursor.fetchone()
        while row != None:
            self.lan.append([row[0], row[1], row[2], row[3], row[4], row[5]])

            row = cursor.fetchone()

        self.conexao.close()

    def limpaListasRenda(self):
        self.listaRendaAcoes.clear()
        self.listaRendaProventos.clear()
        self.listaRendaDespesas.clear()

    def encheListasRenda(self):
        comprado = self.encheListaRendaAcoes()
        self.encheListaRendaProventos()
        return comprado

    def linhaExistente(self, data):
        linha = (-1)
        for row in self.listaRendaAcoes:
            linha +=1
            if row[0] == data:
                return linha

        return (-1)

    def estabeleceRendimentoPorAcoes(self):
        saldoQtde = 0
        aux = self.sigla
        saldoValor = 0.0
        resultado = 0.0
        precomedio = 0.0
        compras = 0.0
        vendas = 0.0
        negocios = 0
        linha = 0
        listaProvisoria = []
        for  row in self.lan:
            dataOperacao = row[1]
            numoperacao = devolveInteger(row[2])
            valorOperacao = devolveFloat(row[4])
            qtdeOperacao = devolveInteger(row[3])
            valorCompraStr = ''
            valorVendaStr = ''
            ganho = 0.0
            strGanho = ""
            strResultado = ''
            resultado = 0.0
            if numoperacao == 1:
                totalOperacao = qtdeOperacao * valorOperacao
                compras += totalOperacao
                if precomedio == 0:
                    precomedio = valorOperacao
                else:
                    precomedio = ((precomedio * saldoQtde) + totalOperacao) / (saldoQtde + qtdeOperacao)
                saldoQtde += qtdeOperacao

            else:
                totalOperacao = valorOperacao * qtdeOperacao
                vendas += totalOperacao
                resultado = totalOperacao - (qtdeOperacao * precomedio)
                #resultado = float(int(resultado*100.0)) / 100.0

                saldoQtde -= qtdeOperacao
                if saldoQtde == 0:
                    precomedio = 0.0

                if resultado != 0.0:
                    listaProvisoria.append([dataOperacao, resultado])
        comprado = saldoQtde * precomedio
        return comprado, compras, vendas, listaProvisoria

    def encheListaRendaAcoes(self):
        #a.dataoperacao, a.operacao, a.qtdeoperacao, a.valoroperacao
        comprado, compras, vendas, listaProvisoria = self.estabeleceRendimentoPorAcoes()
        for row in listaProvisoria:
            dataOperacao = row[0].strftime("%Y/%m")
            #valorRendimento = float(int(row[1] * 100.0) / 100.0)
            valorRendimento = float(row[1])
            if len(self.listaRendaAcoes) == 0:
                self.listaRendaAcoes.append([dataOperacao, valorRendimento])
            else:
                indice = next((i for i, linha in enumerate(self.listaRendaAcoes) if linha[0] == dataOperacao), -1)
                if indice < 0:
                    self.listaRendaAcoes.append([dataOperacao, valorRendimento])
                else:
                    self.listaRendaAcoes[indice][1] += valorRendimento
        return comprado, compras, vendas

    def encheListaRendaProventos(self):
        for row in self.proventos:
            dataOperacao = row[1].strftime("%Y/%m")
            valorRendimento = float(int(row[2] * 100.0) / 100.0)
            if len(self.listaRendaProventos) == 0:
                self.listaRendaProventos.append([dataOperacao, valorRendimento])
            else:
                for item in self.listaRendaProventos:
                    if item[0] == dataOperacao:
                        item[1] += valorRendimento
                        break
                else:
                    self.listaRendaProventos.append([dataOperacao, valorRendimento])

    def busca_radar(self, siglaAtivo):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()
        lista = []
        try:
            clausulasql = "select r.id, r.datacom, r.dataprovavel, r.tipoprovento, r.dy, r.valorprovento from radar as r " \
                          "join ativo as a on a.id = r.idativo " \
                          "where upper(a.sigla) =  upper('" + siglaAtivo + "');"
            cursor.execute(clausulasql)

            lista = self.conexao.cursor.fetchall()

        except  Exception as e:
            lista = []
        finally:
            self.conexao.close()
            return lista

    def setid_ativo(self, arg):
        self.id_ativo = arg
    def setrazao_social(self, arg):
        if arg is None:
            arg = ''
        arg = arg.title()
        self.razao_social = arg[0:self.tamrazao_social]
    def setsigla(self, arg):
        if arg is None:
            arg = ''
        self.sigla = arg[0:self.tamsigla]

    def sqlBuscaTamanho(self, coluna):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        clausulaSql = "select character_maximum_length from INFORMATION_SCHEMA.COLUMNS "
        clausulaSql += "where table_catalog = '" + self.nome_base + "' and table_name = 'ativo'"
        clausulaSql += "and column_name = '" + coluna + "';"

        try:
            cursor.execute(clausulaSql)
            row = cursor.fetchone()
            tam = 0
            if row != None:
                tam = row[0]
            self.conexao.close()
            return tam
        except:
            self.conexao.close()
            return 0

    @staticmethod
    def mc_verifica_ativo_por_id(id):
        conexao = Ativo.getConexao()
        cursor = conexao.cursor()
        cursor.execute("SELECT id, razaosocial, sigla, interesse, idbolsa FROM ativo WHERE id = %s", (id,))
        lista = cursor.fetchone()
        conexao.close()
        return lista
    
    @staticmethod
    def mc_verifica_ativo_por_sigla(arg):
        conexao = Ativo.getConexao()
        cursor = conexao.cursor()
        cursor.execute("SELECT id, razaosocial, sigla, interesse, idbolsa FROM ativo WHERE upper(sigla) = upper(%s)", (arg,))
        lista = cursor.fetchone()
        conexao.close()
        return lista

    @staticmethod
    def devolveSiglaAtivo(id):
        conexao = Ativo.getConexao()
        cursor = conexao.cursor()
        cursor.execute("SELECT sigla FROM ativo WHERE id = %s", (id,))
        row = cursor.fetchone()
        if row: return row[0]
        else: return None

    @staticmethod
    def mc_devolve_nome_ativo_by_sigla(arg):
        conexao = Ativo.getConexao()
        cursor = conexao.cursor()
        cursor.execute("SELECT razaosocial FROM ativo WHERE upper(sigla) = upper(%s)", (arg,))
        row = cursor.fetchone()
        conexao.close()
        if row: return row[0]
        else: return None

    @staticmethod
    def devolveLancamentosNaData(data, conta):
        conexao = Ativo.getConexao()
        cursor = conexao.cursor()

        clausulaSql = 'select an.id, an.idativo, a.sigla, a.razaosocial, an.valoroperacao, an.qtdeoperacao, ' \
                      'an.dataoperacao, an.idconta, c.nomeconta, an.dataehorainsert, an.operacao, an.simulado from ativonegociado as an ' \
                      'join ativo as a on an.idativo = a.id join conta as c on an.idconta = c.id ' \
                      'where an.dataoperacao = \'' + data + '\' and an.idconta = ' + str(conta) + ' ' \
                      'order by a.sigla, an.dataehorainsert;'

        cursor.execute(clausulaSql)
        lista = cursor.fetchall() 
        conexao.close()
        return lista

    @staticmethod
    def buscaListaDeAtivosDeInteresse():
        conexao = Ativo.getConexao()
        cursor = conexao.cursor()
        
        clausulaSql = 'select id, sigla, razaosocial, interesse from ativo where interesse = 1 order by sigla;'

        cursor.execute(clausulaSql)
        lista = cursor.fetchall() 
        conexao.close()
        return lista
        
    @staticmethod
    def get_ultima_cotacao(arg):
        """ Obtém a última cotação do ativo usando Yahoo Finance """
        sigla = str(arg).upper() + ".SA"
        try:
            ativo = yf.Ticker(sigla)
            cotacao = ativo.history(period="1d")["Close"].iloc[-1]
            return cotacao
        except Exception as e:
            return 0.0

    @staticmethod
    def get_valor_mercado_yfinance(ticker, bolsa):
        """ Obtém o valor de mercado da empresa a partir do Yahoo Finance. """
        try:
            if bolsa == 'B3': sufixo = ".SA"
            elif bolsa == 'NASDAQ': sufixo = ""
            elif bolsa == 'NYSE': sufixo = ""
            elif bolsa == 'MILAN': sufixo = ".MI"
            else: sufixo = ""
            
            sigla = str(ticker).upper() + str(sufixo).upper()
            ativo = yf.Ticker(sigla)
            market_cap = ativo.info.get("marketCap")

            if market_cap:
                return market_cap
            else:
                return 0.0
        except Exception as e:
            return 0.0

    @staticmethod
    def get_cotacao_por_data(arg, data):
        """ Obtém a cotação do ativo para uma data específica usando Yahoo Finance """
        sigla = str(arg).upper() + ".SA"
        data_inicio = data
        data_fim = data_inicio + timedelta(days=1)  # Adiciona um dia ao 'end'
        data_str_inicio = data_inicio.strftime("%Y-%m-%d")
        data_str_fim = data_fim.strftime("%Y-%m-%d")
        try:
            ativo = yf.Ticker(sigla)
            #cotacoes = ativo.history(start=str(data), end=str(data))["Close"]
            #cotacoes = ativo.history(start=data_inicio.strftime("%Y-%m-%d"),
            #                        end=data_fim.strftime("%Y-%m-%d"))["Close"]
            cotacoes = ativo.history(start=data_str_inicio, end=data_str_fim)["Close"]

            if not cotacoes.empty:
                return cotacoes.iloc[-1]  # Retorna a última cotação do dia especificado
            else:
                return 0.0  # Nenhuma cotação disponível para essa data

        except Exception as e:
            print(f"Erro ao obter cotação: {e}")
            return 0.0
    
    @staticmethod
    def mc_mudainteresse_do_ativo(sigla, interesse):
        conexao = Ativo.getConexao()
        cursor = conexao.cursor()
        cursor.execute("UPDATE ativo SET interesse = %s WHERE upper(sigla) = upper(%s)", (interesse, sigla))
        conexao.commit()
        conexao.close()

    @staticmethod
    def mc_busca_radar(filter_dy=None, order_by="datacom", filter_interesse=-1, filter_dias=0, sigla_bolsa=None):
        conexao = Ativo.getConexao()
        clausulaSql = ''
        lista = None
        filtro = 0

        if order_by == 'sigla': sqlorderby = 'a.sigla, r.datacom, r.dataprovavel'
        elif order_by == 'razaosocial': sqlorderby = 'a.razaosocial, r.datacom, r.dataprovavel'
        elif order_by == 'tipoprov': sqlorderby = 'r.tipoprovento, a.sigla, r.datacom, r.dataprovavel'
        elif order_by == 'datacom': sqlorderby = 'r.datacom, a.sigla, r.dataprovavel'
        elif order_by == 'datapgto': sqlorderby = 'r.dataprovavel, a.sigla, r.datacom'
        elif order_by == 'dy': sqlorderby = 'r.dy desc, r.datacom, r.dataprovavel'
        else: sqlorderby = 'r.datacom, a.sigla, r.dataprovavel'

        if filter_interesse:
            filtro=filter_interesse
        if filter_dy is None: 
            clausulaSql = 'SELECT r.id, a.sigla, a.razaosocial, r.tipoprovento, r.datacom, r.dataprovavel, ' \
                'r.valorprovento, r.ultimacotacao, r.dy, a.interesse FROM radar r ' \
                'JOIN ativo as a ON r.idativo = a.id ' \
                'where a.idbolsa = (select id from bolsa where sigla = \'' + sigla_bolsa + '\') and '\
                'a.interesse >= ' + str(filtro) + ' and ' \
                'r.datacom >= CURRENT_DATE - INTERVAL \'' + str(filter_dias) + ' days\' ' \
                'order by ' + sqlorderby      # r.datacom, a.sigla, r.dataprovavel'
        else:
            clausulaSql = 'SELECT r.id, a.sigla, a.razaosocial, r.tipoprovento, r.datacom, r.dataprovavel, ' \
                'r.valorprovento, r.ultimacotacao, r.dy, a.interesse FROM radar r ' \
                'JOIN ativo a ON r.idativo = a.id ' \
                'where r.datacom >= CURRENT_DATE - INTERVAL \'' + str(filter_dias) + ' days\' and ' \
                'a.idbolsa = (select id from bolsa where sigla = \'' + sigla_bolsa + '\') and '\
                'a.interesse >= ' + str(filtro) + ' and ' \
                'r.dy >= ' + str(filter_dy) + ' ' \
                'order by ' + sqlorderby      #r.datacom, a.sigla, r.dataprovavel'

        try:
            with conexao.cursor() as cursor:
                cursor.execute(clausulaSql)
                lista = cursor.fetchall()

        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler lançamentos de Capital', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
        
        conexao.close()
        return lista



def main():
    ativo = Ativo()
    ativo.populaAtivoBySigla('VALE3')
    print('sigla = ')
    print(ativo.sigla)

    print('acabou')


if __name__ == '__main__':
    main()